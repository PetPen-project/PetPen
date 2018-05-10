$(function(){
  var modal = $(".preview-modal");
  var descriptionModal = $(".description-modal");
  $("button[name=preview]").click(function(){
    console.log("http://www.petpen.org/media/demo/" + $(this).data("title") + ".png");
    //$(".preview-modal img").attr('src',"http://140.109.18.113:8000/media/vgg.png");
    var url = "http://www.petpen.org/media/"+$(this).data("title")+".png";
    $.get(url)
    .done(function() { 
    $(".preview-modal img").attr('src',"http://www.petpen.org/media/"+$(this).data("title")+".png");
        // exists code 
    }).fail(function() {
      $(".preview-modal").html("preview not available");
        // not exists code
    })
    //$(".preview-modal img").attr('src',"http://www.petpen.org/media/"+$(this).data("title")+".png");
    modal.show();
    $(document).mouseup(function(e){
      var container = $(".preview-modal img");
      if (!container.is(e.target) && container.has(e.target).length === 0){
        modal.hide();
      }
    });
  });
  $("p[name=description-link]").click(function(){
    $.ajax({
      async: false,
      type: "GET",
      url: window.location.href,
      data: {description: $(this)[0].dataset.id},
      success: function(data){
    $(".description-modal p").html(data);
      }
    });
    descriptionModal.show();
    $(document).mouseup(function(e){
      var container = $(".description-modal p");
      if (!container.is(e.target) && container.has(e.target).length === 0){
        descriptionModal.hide();
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
