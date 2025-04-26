# Django Authentication API (Mobile & OTP Based)
A Django RESTful API for user authentication using mobile numbers and one-time passwords (OTP). 
Users can register via mobile, verify OTP, complete their profile, and login using password authentication.
## Features
- Request OTP for mobile number authentication
- Verify OTP within 1 minutes (expiration control)
- User registration and profile completion
- Login with mobile number and password
- IP and mobile blocking system after 3 failed attempts
- Clean, validated inputs with meaningful responses
## API Testing with Postman
- Import the provided Postman collection located in the `/postman/authentication_api_collection.json` file.
- Use the following endpoints:
  - `POST /api/accounts/request-mobile/` : Request OTP
  - `POST /api/accounts/verify-otp/` : Verify OTP
  - `POST /api/accounts/complete-profile/` : Complete user profile
  - `POST /api/accounts/password-login/` : Login with mobile and password
    
## Input Validation Rules
- Mobile number must start with 09 and be 11 digits (Iranian format).
- OTP must be a 6-digit number.
- Password must be at least 6 characters.
- Email must be a valid email address.

