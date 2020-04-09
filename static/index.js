    // buttons to click
    var showLoginButton = document.getElementsByClassName('list-join-button')[0];
    var showSignupButton = document.getElementsByClassName('auth-form__signup')[0];
    var closeButton0 = document.getElementsByClassName('close-button')[0];
    var closeButton1 = document.getElementsByClassName('close-button')[1];
    var bottomJoin = document.getElementsByClassName('top-left-cube__item')[0];


    // events after clicking
    var loginSectionShown = document.getElementsByClassName('auth-section')[0];
    var signupSectionShown = document.getElementsByClassName('signup-section')[0];

    // events functions
    showLoginButton.onclick = function() {
        loginSectionShown.style.display = 'grid';
    };
    bottomJoin.onclick = function() {
        signupSectionShown.style.display = 'grid';
    }
    showSignupButton.onclick = function() {
            loginSectionShown.style.display = 'none';
            signupSectionShown.style.display = 'grid';
    };
    closeButton0.onclick = function() {
        loginSectionShown.style.display = 'none';
        signupSectionShown.style.display = 'none';
    }
    closeButton1.onclick = function() {
        loginSectionShown.style.display = 'none';
        signupSectionShown.style.display = 'none';
    }