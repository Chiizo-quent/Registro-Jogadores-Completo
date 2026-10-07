// Mostra a prévia da imagem assim que a pessoa escolhe o arquivo (antes de salvar)
document.querySelectorAll("input[type=file][data-preview]").forEach(input => {
    input.addEventListener("change", () => {
        const img = document.getElementById(input.dataset.preview)
        const arquivo = input.files[0]
        if (arquivo) {
            img.src = URL.createObjectURL(arquivo)   // cria um endereço temporário para o arquivo
            img.hidden = false
        }
    })
})
