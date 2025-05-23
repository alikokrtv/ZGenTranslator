import requests
import sys
import re

def test_login():
    """Test the login functionality"""
    # URL for login
    login_url = "http://127.0.0.1:5000/login"
    
    # First, get the login page to verify it's working
    print("Testing connection to login page...")
    try:
        response = requests.get(login_url)
        if response.status_code == 200:
            print(f"✅ Login page accessible (status code: {response.status_code})")
        else:
            print(f"❌ Error accessing login page (status code: {response.status_code})")
            return
    except Exception as e:
        print(f"❌ Error connecting to server: {str(e)}")
        print("Make sure the application is running first!")
        return
    
    # Extract the form to check its structure
    form_pattern = re.compile(r'<form[^>]*id="login-form"[^>]*>(.*?)</form>', re.DOTALL)
    form_match = form_pattern.search(response.text)
    
    if form_match:
        form_html = form_match.group(0)
        print("\n=== LOGIN FORM HTML ===")
        print(form_html)
        print("=======================\n")
    else:
        print("❌ Couldn't find the login form in the HTML")
    
    # Use our created test user
    test_user = "testuser"
    test_pass = "testpassword"
    
    print(f"\nAttempting login with test credentials (username: {test_user})...")
    try:
        # Create login data
        login_data = {
            "username": test_user,
            "password": test_pass
        }
        
        # Debug the data being sent
        print(f"Sending data: {login_data}")
        
        # Start a session to handle cookies
        with requests.Session() as session:
            # Submit the login form
            login_response = session.post(login_url, data=login_data, allow_redirects=True)
            
            # Check response status
            print(f"Login response status code: {login_response.status_code}")
            
            # Check if redirected (successful login should redirect)
            is_redirected = login_response.url != login_url
            print(f"Redirected: {is_redirected}")
            print(f"Current URL: {login_response.url}")
            
            # Check cookies to see if session was set
            cookies = session.cookies.get_dict()
            print(f"Cookies after login: {cookies}")
            
            # Try accessing a protected page to verify login state
            profile_response = session.get("http://127.0.0.1:5000/profile")
            print(f"Profile page status code: {profile_response.status_code}")
            print(f"Profile page URL: {profile_response.url}")
            
            if "Profilim" in profile_response.text:
                print("✅ Successfully accessed profile page - Login confirmed!")
            else:
                print("❌ Could not access profile page - Login unsuccessful")
                
            # Look for flash messages in the response
            if "Giriş başarılı" in login_response.text:
                print("✅ Success message found - Login successful!")
            elif "Kullanıcı adı veya şifre hatalı" in login_response.text:
                print("❌ Error message found - Login failed")
                
            # Check if we're still on the login page
            if 'form id="login-form"' in login_response.text:
                print("⚠️ Login form is still visible - Login might have failed")
            else:
                print("✅ Login form is not visible - Likely logged in successfully")
    except Exception as e:
        print(f"❌ Error during login test: {str(e)}")

if __name__ == "__main__":
    test_login() 