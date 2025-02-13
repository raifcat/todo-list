
const username = document.getElementById("username");
const password = document.getElementById("password");
const conpassword = document.getElementById("conpassword");

const userErrorText = document.getElementById("user-error-text");
const passErrorText = document.getElementById("pass-error-text");
const conpassErrorText = document.getElementById("conpass-error-text");

const signupButton = document.getElementById("signup-button");

async function Signup() {

    let res = undefined;

    const response = await fetch(`http://127.0.0.1:8000/create-user/`, {

        method: "POST",
        body: JSON.stringify({
            "username": `${username.value}`,
            "password": `${password.value}`,
            "conpassword": `${conpassword.value}`
        }),
        headers: { "Content-type": "application/json; charset=UTF-8" }

    })
        //.then((response) => res = response)
        //.then((json) => res = json);
    const content = await response;

    return [await content.status, await content.json()]

}

signupButton.addEventListener("click", SignupButtonClicked)

function SignupButtonClicked(){
    (async () => {
        response = await Signup()  
        console.log(response[1]["detail"])

        if (response[0] == 400){
            createErrors(response[1]["detail"])
        }

        if (response[0] == 200){
            location.reload()
        }
    })()
}

const errorList = document.getElementById("error-text-list")

function createErrors(errors){

    errorList.innerHTML = ""

    for (const error in errors) {

        const errorText = document.createElement("p")
        errorText.textContent = errors[error]
        errorText.classList.add("error-text")
        errorList.appendChild(errorText)

    }
    

}



/*

let conpasswordErrors = [];
let usernameErrors = [];
let passwordErrors = [];

function disableButton(){

    if (usernameErrors.length + passwordErrors.length + conpasswordErrors.length) {
        signupButton.disabled = true;
    } else {
        signupButton.disabled = false;
    }

}

function checkConpassErrors() {

    conpasswordErrors = [];

    if (conpassword.value != password.value) {
        conpasswordErrors.push("Passwords don't match");
    }

    conpassErrorText.innerHTML = conpasswordErrors[0] ?? "";

    disableButton()

}

function checkUsernameErrors() {

    usernameErrors = [];

    if (username.value.length > 20) {
        usernameErrors.push("Username must be 3-20 chars long");
    }
    if (username.value.length < 3) {
        usernameErrors.push("Username must be 3-20 chars long");
    }

    userErrorText.innerHTML = usernameErrors[0] ?? "";

    disableButton()

}

function checkPasswordErrors() {

    passwordErrors = [];

    if (password.value.length < 8) {
        passwordErrors.push("Password must be 8 or more chars long");
    }

    if (password.value.length > 255) {
        passwordErrors.push("Password cant be longer than 255 chars");
    }

    if (conpassword.value == password.value) {
        conpasswordErrors = [];
        conpassErrorText.innerHTML = conpasswordErrors[0] ?? "";
    }

    passErrorText.innerHTML = passwordErrors[0] ?? "";

    disableButton()

}

username.addEventListener("change", checkUsernameErrors);
password.addEventListener("change", checkPasswordErrors);
conpassword.addEventListener("change", checkConpassErrors);*/