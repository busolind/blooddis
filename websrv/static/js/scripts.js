let resultDiv = document.getElementById("result");
let form = document.getElementById("imguploadform");

function resetResultDiv() {
  resultDiv.className = "d-none";
  resultDiv.innerHTML = "";
}

form.onsubmit = async (e) => {
  e.preventDefault();
  const url = form.action;

  try {
    const formData = new FormData(form);
    await fetch(url, {
      method: "POST",
      body: formData,
    }).then((response) => {
      if (response.status == 200) {
        response.json().then((data) => {
          console.log(data);

          resultDiv.classList.remove("d-none");
          resultDiv.innerHTML = "";
          resultDiv.classList.add("border", "border-success", "rounded", "animate__animated", "animate__fadeIn");
          var innerp = document.createElement("h2");
          innerp.innerText = "Your prediction is: " + data["prediction"];
          innerp.classList.add("text-info");
          innerp.classList.add("animate__animated", "animate__zoomIn");
          resultDiv.appendChild(innerp);
        });
      } else {
        resetResultDiv();
        alert("Prediction could not be made");
      }
    });
  } catch (error) {
    resetResultDiv();
    console.error(error);
    alert("An error occured in the request");
  }
};
