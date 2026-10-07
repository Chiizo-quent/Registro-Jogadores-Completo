function checkUser(){
    const username = document.querySelector("#inputUsername").value.trim()
    const aviso = document.querySelector("#avisoUsuario")
    if(username.length < 1){
        aviso.textContent = ""
        return
    }
    fetch(`/checkUser?usernameCheck=${encodeURIComponent(username)}`)
        .then(response => response.json())   // transforma a resposta do Python em objeto JS
        .then(data => {                       // data.verify é o True/False que o Python mandou
            aviso.textContent = data.verify ? "Esse usuário já existe" : ""
        })
}
