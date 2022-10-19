# Charts-Core

# How to test locally
1. Install prerequisites as specified in tests requirements.txt
2. in charts\charts\core type "helm template ." make sure the template renders correctly
3. in charts\charts\core type "pytest" all tests should pass

# How to debug in VS code
https://code.visualstudio.com/docs/python/testing
test discovery in subfolders is based on existence of __init__.py file
to run tests succesfully you need to set test working directory go to File->Preferences->settings, search Tests, select Python and find "Optional working directory for tests." Set it to charts\core