let form = document.getElementById('imguploadform');

let resultModal = new bootstrap.Modal(document.getElementById('resultModalCenter'), {});
let resultModalBody = document.getElementById('resultModalBody');

form.onsubmit = async (e) => {
  e.preventDefault();
  const url = form.action;

  try {
    const formData = new FormData(form);
    await fetch(url, {
      method: 'POST',
      body: formData,
    }).then((response) => {
      if (response.status == 200) {
        response.json().then((data) => {
          //console.log(data);
          resultModalBody.innerText = 'Your result is: ' + data['prediction'];
          resultModal.show();
        });
      } else {
        alert('Prediction could not be made');
      }
    });
  } catch (error) {
    console.error(error);
    alert('An error occured in the request');
  }
};
