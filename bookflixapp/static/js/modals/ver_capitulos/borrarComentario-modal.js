//pasarle el id del comentario al popup (no encontre otra forma)
$('#borrarComentario-modal').on('show.bs.modal', function (event) {
  var myVal = $(event.relatedTarget).data('val2');
  $(this).find(".pk2").val(myVal);
});
