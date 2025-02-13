
const username = document.getElementById("username");
const password = document.getElementById("password");

//const userErrorText = document.getElementById("user-error-text");
//const passErrorText = document.getElementById("pass-error-text");

const loginButton = document.getElementById("login-button");

async function Signup() {

    let res = undefined;

    const response = await fetch(`http://127.0.0.1:8000/login-user/`, {

        method: "POST",
        body: JSON.stringify({
            "username": `${username.value}`,
            "password": `${password.value}`
        }),
        headers: { "Content-type": "application/json; charset=UTF-8" }

    })
    //.then((response) => res = response)
    //.then((json) => res = json);
    const content = await response;

    return [await content.status, await content.json()]

}

loginButton.addEventListener("click", SignupButtonClicked)

function SignupButtonClicked() {
    (async () => {
        response = await Signup()
        console.log(response[1]["detail"])

        if (response[0] == 400) {
            createErrors(response[1]["detail"])
        }

        if (response[0] == 200) {
            location.reload()
        }
    })()
}

const errorList = document.getElementById("error-text-list")

function createErrors(errors) {

    errorList.innerHTML = ""

    for (const error in errors) {

        const errorText = document.createElement("p")
        errorText.textContent = errors[error]
        errorText.classList.add("error-text")
        errorList.appendChild(errorText)

    }


}