from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UpdateUserForm, CustomPasswordChangeForm

@login_required
def profile_settings(request):
    if request.method == 'POST':
        u_form = UpdateUserForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile_settings')
    else:
        u_form = UpdateUserForm(instance=request.user)

    return render(request, 'profile_settings.html', {
        'u_form': u_form
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Keeps user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {
        'form': form
    })


@login_required
def settings(request):
    return render(request, 'settings.html')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileImageForm

@login_required
def upload_profile_picture(request):
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('upload_profile_picture')
    else:
        form = ProfileImageForm(instance=request.user.profile)
    
    return render(request, 'upload_profile_picture.html', {'form': form})

