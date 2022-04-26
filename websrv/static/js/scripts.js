var form = document.getElementById('imguploadform');

form.onsubmit = async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const url = form.action;

  try {
    const formData = new FormData(form);
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });
    response.json().then((data) => {
      console.log(data);
      var div = document.getElementById('result');
      div.classList.remove('d-none');
      div.innerHTML = '';
      var innerp = document.createElement('h2');
      innerp.innerText = 'Your prediction is: ' + data['prediction'];
      innerp.classList.add('text-info');
      innerp.classList.add('animate__animated', 'animate__zoomIn');
      div.appendChild(innerp);
    });
  } catch (error) {
    console.error(error);
    alert('Prediction could not be made');
  }
};
