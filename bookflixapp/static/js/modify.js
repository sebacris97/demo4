
  first_name = document.getElementById("id_first_name");
  first_name.setAttribute("class","form-control");
  first_name.setAttribute("placeholder","Ingrese su nombre");
  first_name.required = false;

  last_name = document.getElementById("id_last_name");
  last_name.setAttribute("class","form-control");
  last_name.setAttribute("placeholder","Ingrese su apellido");
  last_name.required = false;

  email = document.getElementById("id_email");
  email.setAttribute("class","form-control");
  email.setAttribute("placeholder","Ingrese su email");
  email.required = false;

  fecha_de_nacimiento = document.getElementById("id_fecha_de_nacimiento");
  fecha_de_nacimiento.setAttribute("class","form-control");
  fecha_de_nacimiento.setAttribute("max","2100-12-31");
  fecha_de_nacimiento.setAttribute("min","1900-01-01");
  fecha_de_nacimiento.setAttribute("type","date");
  fecha_de_nacimiento.required = false;

  tarjeta = document.getElementById("id_tarjeta");
  tarjeta.setAttribute("type","text");
  tarjeta.setAttribute("class","form-control");
  tarjeta.setAttribute("placeholder","Ingrese el numero de su tarjeta de credito");
  tarjeta.required = false;
