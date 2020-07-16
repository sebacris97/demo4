//pasarle el id del comentario al popup (no encontre otra forma)
$('#editarComentario-modal').on('show.bs.modal', function (event) {
  var myVal = $(event.relatedTarget).data('val');
  $(this).find(".pk").val(myVal);
});


//poner el cursor del popup modificar comentario directamente para escribir
$('#editarComentario-modal').on('shown.bs.modal', function () {
  $('#id_texto').trigger('focus')
})


