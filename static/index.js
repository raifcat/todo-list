const tname = document.getElementById("form-name");
const desc = document.getElementById("form-desc");

async function CreateItem(){

    let res = undefined;

    const response = await fetch('http://127.0.0.1:8000/create-item', {

        method: "POST",
        body: JSON.stringify({
            "name": `${tname.value}`, "desc": `${desc.value}`
        }),
        headers: { "Content-type": "application/json; charset=UTF-8" }

    })
    const content = await response;

    return [await content.status, await content.json()]
    
}

const formButton = document.getElementById("form-button");

formButton.addEventListener("click", formButtonClicked);

function formButtonClicked() {
    (async () => {
        response = await CreateItem()
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

tname.addEventListener("input", FormInputChange)
desc.addEventListener("input", FormInputChange)

nameLimit = document.getElementById("name-limit")
descLimit = document.getElementById("desc-limit")

function FormInputChange(){

    tnameLength = tname.value.length
    descLength = desc.value.length

    nameLimit.textContent = `${tnameLength}/50`
    nameLimit.classList.remove("red-text")
    if (tnameLength > 50){
        nameLimit.classList.add("red-text")
    }

    descLimit.textContent = `${descLength}/255`
    descLimit.classList.remove("red-text")
    if (descLength > 255) {
        descLimit.classList.add("red-text")
    }

}



/*
async function GetItem(done, start, amount) {

    let res = undefined;

    const response = await fetch(`http://127.0.0.1:8000/get-bulk`, {

        method: "POST",
        body: JSON.stringify({
            "done": `${done}`,
            "offset": `${start}`,
            "amount": `${amount}`
        }),
        headers: { "Content-type": "application/json; charset=UTF-8" }

    })
    const content = await response;

    return [await content.status, await content.json()]

}

(async () => {
    response = await GetItem(0, 2, 2)
    console.log(response[1])

})()*/