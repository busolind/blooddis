var form = document.getElementById("imguploadform");

form.onsubmit = async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const url = form.action;

  try {
    const formData = new FormData(form);
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });
    response.json().then((data) => {
      console.log(data);
    });
  } catch (error) {
    console.error(error);
  }
};
