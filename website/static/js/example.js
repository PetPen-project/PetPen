$(function(){
  var modal = $(".preview-modal");
  $("button[name=preview]").click(function(){
    console.log("http://www.petpen.org/media/demo/" + $(this).data("title") + ".png");
    $(".preview-modal img").attr('src',"http://140.109.18.113:8000/media/vgg.png");
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
