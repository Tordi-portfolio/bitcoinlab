from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from .forms import TransactionForm
from .models import *
from .models import Wallet, Transaction
from django.contrib.auth.decorators import user_passes_test
from decimal import Decimal, InvalidOperation
from bs4 import BeautifulSoup
import requests


# Create your views here.


def is_admin(user):
    return user.is_superuser or user.is_staff

def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction created successfully!")
            return redirect('transaction')  # You can change this to a transaction list if needed
    else:
        form = TransactionForm()
    
    return render(request, 'wallet/create_transaction.html', {'form': form})


@login_required
def transaction(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'wallet/transaction.html', {'transactions': transactions})


@login_required
def deposit(request):
    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=request.user)

    wallet_address = wallet.bitcoin_address or "bc1qklfaar303lqxsx3ckfvxf4x8maksyq5hq9vcwh"

    print("WALLET ADDRESS:", wallet_address)  # <--- DEBUG PRINT
    print("WALLET:", wallet)  # <--- DEBUG PRINT

    user_transactions = Transaction.objects.filter(user=request.user, transaction_type='deposit').order_by('-created_at')

    if request.method == 'POST':
        form = DepositConfirmationForm(request.POST, request.FILES)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.save()
            messages.success(request, "Deposit confirmation submitted successfully!")
            return redirect('deposit')
    else:
        form = DepositConfirmationForm()

    return render(request, 'wallet/deposit.html', {
        'wallet': wallet,
        'wallet_address': wallet_address,
        'transactions': user_transactions,
        'form': form,
    })

@login_required
def withdraw(request):
    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        messages.error(request, "Wallet not found.")
        return redirect("balance")

    MIN_WITHDRAW = Decimal("0.001")

    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get("amount", "0"))
        except InvalidOperation:
            messages.error(request, "Invalid withdrawal amount.")
            return redirect("withdraw")

        wallet_address = request.POST.get("wallet_address")

        if amount < MIN_WITHDRAW:
            messages.error(request, f"Minimum withdrawable amount is {MIN_WITHDRAW} BTC.")
        elif amount > wallet.bitcoin_balance:
            messages.error(request, "Insufficient balance.")
        elif not wallet_address:
            messages.error(request, "Wallet address is required.")
        else:
            wallet.bitcoin_balance -= amount
            wallet.save()

            # ✅ Create a PENDING transaction
            Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type="withdrawal",
                address=wallet_address,
                status="pending"  # << HERE!
            )

            messages.success(request, f"Withdrawal of {amount} BTC to {wallet_address} submitted and is pending approval.")
            return redirect("transaction")

    return render(request, "wallet/withdraw.html", {"wallet": wallet})


@user_passes_test(is_admin)
def manage_balances(request):
    users = User.objects.all()
    selected_wallet = None

    if request.method == 'POST':
        user_id = request.POST.get('user')
        new_balance = request.POST.get('balance')

        try:
            user = User.objects.get(id=user_id)
            wallet, created = Wallet.objects.get_or_create(user=user)
            wallet.bitcoin_balance = new_balance
            wallet.save()
            messages.success(request, f"{user.username}'s balance updated to {new_balance} BTC.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

        return redirect('manage_balances')

    # If it's a GET with ?user_id=123, show wallet
    user_id = request.GET.get('user_id')
    if user_id:
        try:
            selected_user = User.objects.get(id=user_id)
            selected_wallet = Wallet.objects.get(user=selected_user)
        except:
            selected_wallet = None

    return render(request, 'wallet/manage_balances.html', {
        'users': users,
        'selected_wallet': selected_wallet,
        'selected_user_id': user_id,
    })


import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet  # adjust if needed


def get_crypto_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,tether,solana,bitcoin-cash,the-open-network,binancecoin,tron,dogecoin,sui,bitget-token,usd-coin",
            "vs_currencies": "usd"
        }
        response = requests.get(url, params=params)
        data = response.json()

        return {
            'btc': f"${data['bitcoin']['usd']:,.2f}",
            'eth': f"${data['ethereum']['usd']:,.2f}",
            'usdt': f"${data['tether']['usd']:,.2f}",
            'sol': f"${data['solana']['usd']:,.2f}",
            'bch': f"${data['bitcoin-cash']['usd']:,.2f}",
            'ton': f"${data['the-open-network']['usd']:,.2f}",
            'bnb': f"${data['binancecoin']['usd']:,.2f}",
            'tron': f"${data['tron']['usd']:,.4f}",
            'doge': f"${data['dogecoin']['usd']:,.4f}",
            'sui': f"${data['sui']['usd']:,.4f}",
            'bgb': f"${data['bitget-token']['usd']:,.4f}",
            'usdc': f"${data['usd-coin']['usd']:,.2f}",
        }

    except Exception as e:
        print("Error getting crypto prices:", e)
        return {
            'btc': "Unavailable",
            'eth': "Unavailable",
            'usdt': "Unavailable",
            'sol': "Unavailable",
            'bch': "Unavailable",
            'ton': "Unavailable",
            'bnb': "Unavailable",
            'tron': "Unavailable",
            'doge': "Unavailable",
            'sui': "Unavailable",
            'bgb': "Unavailable",
            'usdc': "Unavailable",
        }



@login_required
def home(request):
    prices = get_crypto_prices()
    
    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=request.user, bitcoin_balance=0.0)

    context = {**prices, 'wallet': wallet}
    return render(request, 'home.html', context)


@login_required
def balance(request):
    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=request.user, bitcoin_balance=0.0)

    return render(request, 'wallet/balance.html', {'wallet': wallet})

    

def RegisterView(request):

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_data_has_error = False

        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, "Username already exists...")
        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, "Email already exists...")

        if len(password) < 5:
            user_data_has_error = True
            messages.error(request, "Password must be at least 5 characters...")

        if user_data_has_error:
            return redirect('register')
        else:
            new_user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            messages.success(request, "Account created. Login now...")
            return redirect('login')

    return render(request, 'logins/register.html')

def LoginView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            messages.success(request, "Login successfully...")
            return redirect('home')
        else:
            messages.error(request, "Invalid login credentials...")
            return redirect('login')
    return render(request, 'logins/login.html')

def LogoutView(request):
    logout(request)
    messages.success(request, "Logout successfully...")
    return redirect('login')


def ForgotPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
        
            email_message = EmailMessage(
                'Reset your password', # email subject
                email_body,
                settings.EMAIL_HOST_USER, # email sender
                [email] # email  receiver 
            )

            email_message.fail_silently = True
            email_message.send()

            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)

        except User.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')
    return render(request, 'logins/forgot_password.html')


def PasswordResetSent(request, reset_id):

    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'logins/password_reset_sent.html')
    else:
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')

    return redirect('forgot_password')



def ResetPassword(request, reset_id):

    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            else:
                # redirect back to password reset page and display errors
                return redirect('reset-password', reset_id=reset_id)

    
    except PasswordReset.DoesNotExist:
        
        # redirect to forgot password page if code does not exist
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')
        
    return render(request, 'logins/reset_password.html')


from .forms import DepositConfirmationForm
from .models import DepositConfirmation

@login_required
def deposit_form_view(request):
    if request.method == 'POST':
        form = DepositConfirmationForm(request.POST, request.FILES)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.save()
            return render(request, 'wallet/deposit_success.html')
    else:
        form = DepositConfirmationForm()
    return render(request, 'wallet/deposit.html', {'form': form})


@user_passes_test(lambda u: u.is_staff)
def deposit_submissions_admin(request):
    deposits = DepositConfirmation.objects.all().order_by('-submitted_at')
    return render(request, 'wallet/deposit_submissions.html', {'deposits': deposits})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Wallet, Transaction, UserToUserTransfer
from .forms import UserToUserTransferForm

@login_required
def transfer_crypto(request):
    user = request.user
    form = UserToUserTransferForm(request.POST or None)

    # Get current user's transaction history
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')

    if request.method == 'POST' and form.is_valid():
        recipient = form.cleaned_data['recipient_identifier']
        crypto = form.cleaned_data['crypto']
        amount = form.cleaned_data['amount']

        try:
            wallet = Wallet.objects.get(user=user)
            recipient_wallet = Wallet.objects.get(user=recipient)

            if crypto == 'BTC':
                if wallet.bitcoin_balance < amount:
                    raise ValueError("Insufficient BTC balance.")
                wallet.bitcoin_balance -= amount
                recipient_wallet.bitcoin_balance += amount
            elif crypto == 'ETH':
                if wallet.eth_balance < amount:
                    raise ValueError("Insufficient ETH balance.")
                wallet.eth_balance -= amount
                recipient_wallet.eth_balance += amount
            elif crypto == 'USDT':
                if wallet.usdt_balance < amount:
                    raise ValueError("Insufficient USDT balance.")
                wallet.usdt_balance -= amount
                recipient_wallet.usdt_balance += amount
            elif crypto == 'TON':
                if wallet.ton_balance < amount:
                    raise ValueError("Insufficient TON balance.")
                wallet.ton_balance -= amount
                recipient_wallet.ton_balance += amount
            elif crypto == 'SOL':
                if wallet.solana_balance < amount:
                    raise ValueError("Insufficient SOL balance.")
                wallet.solana_balance -= amount
                recipient_wallet.solana_balance += amount

            elif crypto == 'BNB':
                if wallet.bnb_balance < amount:
                    raise ValueError("Insufficient BNB balance.")
                wallet.bnb_balance -= amount
                recipient_wallet.bnb_balance += amount
            
            elif crypto == 'TRON':
                if wallet.tron_balance < amount:
                    raise ValueError("Insufficient tron balance.")
                wallet.tron_balance -= amount
                recipient_wallet.tron_balance += amount

            elif crypto == 'DOGE':
                if wallet.doge_balance < amount:
                    raise ValueError("Insufficient doge balance.")
                wallet.doge_balance -= amount
                recipient_wallet.doge_balance += amount

            elif crypto == 'SUI':
                if wallet.sui_balance < amount:
                    raise ValueError("Insufficient sui balance.")
                wallet.sui_balance -= amount
                recipient_wallet.sui_balance += amount

            elif crypto == 'BGB':
                if wallet.bgb_balance < amount:
                    raise ValueError("Insufficient bgb balance.")
                wallet.bgb_balance -= amount
                recipient_wallet.bgb_balance += amount

            elif crypto == 'USDC':
                if wallet.usdc_balance < amount:
                    raise ValueError("Insufficient usdc balance.")
                wallet.usdc_balance -= amount
                recipient_wallet.usdc_balance += amount


            wallet.save()
            recipient_wallet.save()

            # Record in UserToUserTransfer
            UserToUserTransfer.objects.create(
                sender=user,
                recipient=recipient,
                crypto=crypto,
                amount=amount,
                status='completed'
            )

            # Record in Transaction history
            Transaction.objects.create(
                user=user,
                transaction_type='withdrawal',
                amount=amount,
                address=f"Sent to {recipient.username}",
                status='completed'
            )

            Transaction.objects.create(
                user=recipient,
                transaction_type='deposit',
                amount=amount,
                address=f"Received from {user.username}",
                status='completed'
            )

            messages.success(request, f"{amount} {crypto} sent to {recipient.username} successfully!")
            return redirect('transfer_crypto')

        except ValueError as e:
            messages.error(request, str(e))
        except Wallet.DoesNotExist:
            messages.error(request, "Wallet not found.")

    return render(request, 'wallet/transfer_crypto.html', {
        'form': form,
        'transactions': transactions
    })


def btc(request):
    return render(request, 'deposit/btc.html')

def eth(request):
    return render(request, 'deposit/eth.html')

def sol(request):
    return render(request, 'deposit/sol.html')

def usdt(request):
    return render(request, 'deposit/usdt.html')

def ton(request):
    return render(request, 'deposit/ton.html')

def bnb(request):
    return render(request, 'deposit/bnb.html')

def tron(request):
    return render(request, 'deposit/tron.html')

def doge(request):
    return render(request, 'deposit/doge.html')

def sui(request):
    return render(request, 'deposit/sui.html')

def bgb(request):
    return render(request, 'deposit/bgb.html')

def usdc(request):
    return render(request, 'deposit/usdc.html')

def airdrop(request):
    return render(request, 'airdrop.html')


from django.utils import timezone
from django.shortcuts import render
from .models import Wallet
from datetime import timedelta


def dashboard(request):
    wallet = Wallet.objects.get(user=request.user)
    next_bonus_time = wallet.last_bonus_added + timedelta(hours=24)
    return render(request, 'dashboard.html', {'wallet': wallet, 'next_bonus_time': next_bonus_time})
