$(function(){
  var modal = $(".preview-modal");
  var descriptionModal = $(".description-modal");
  $("p.description img").click(function(){
    $(".preview-modal").html($(this).clone());
    modal.show();
    $(document).mouseup(function(e){
      var container = $(".preview-modal img");
      if (!container.is(e.target) && container.has(e.target).length === 0){
        modal.hide();
      }
    });
  });
  $('.error-message .close').click(function(){
    $('.error-message').remove();
  });
  $('.info-message .close').click(function(){
    $('.info-message').remove();
  });
});
