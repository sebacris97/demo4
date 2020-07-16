

//desaparecer mensaje despues de 5seg
  setTimeout(fade_out, 2300);
  function fade_out() {
  $(".mensaje").fadeOut("slow")
  }


//mostrar boton cuando pongo mouse arriba
$(document).ready(function () {
                $(document).on('mouseenter', '.card', function () {
                    $(this).find(".boton").show();
                }).on('mouseleave', '.card', function () {
                    $(this).find(".boton").hide();
                });
            });


