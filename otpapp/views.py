from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
import random
from django.core.mail import send_mail
from .models import OTPRecord

def home(request):
    return render(request,'otpapp/home.html')
def request_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # 1. Generate 6-digit code
        otp_code = str(random.randint(100000, 999999))
        
        # 2. Save to database
        OTPRecord.objects.update_or_create(
            email=email,
            defaults={'otp': otp_code, 'created_at': timezone.now()}
        )
        
        # 3. Send Email
        send_mail(
            'Your Registration Code',
            f'Your OTP is: {otp_code}. It expires in 5 minutes.',
            'noreply@yourdomain.com',
            [email],
            fail_silently=False,
        )
        
        # 4. Save email to session so the next page knows who is verifying
        request.session['registration_email'] = email
        
        return redirect('verify_otp')
        
    return render(request, 'otpapp/request_otp.html')

def verify_otp(request):
    # Retrieve the email from the session
    email = request.session.get('registration_email')
    
    # If there is no email in the session, kick them back to step 1
    if not email:
        messages.error(request, "Please start the registration process first.")
        return redirect('request_otp')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        
        try:
            record = OTPRecord.objects.get(email=email)
            
            if record.is_expired():
                messages.error(request, "OTP has expired. Please request a new one.")
                return redirect('request_otp')
                
            if record.otp == entered_otp:
                # SUCCESS! Create the actual User account here.
                # Example: User.objects.create_user(email=email, ...)
                
                # Cleanup: Delete the used OTP and clear the session
                record.delete() 
                del request.session['registration_email']
                
                messages.success(request, "Registration successful!")
                return redirect('home_page') # Change this to your home or login URL
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                
        except OTPRecord.DoesNotExist:
            messages.error(request, "No OTP found for this email.")
            return redirect('request_otp')

    return render(request, 'otpapp/verify_otp.html', {'email': email})