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
  $('.exampleCopyForm').submit(function(e){
    e.preventDefault();
    $('#example-processing').css('display','block');
    var data = $(this).serialize();
    var type = $(this).attr('method');
    //var data = new FormData($(this)[0]);
    setTimeout(function(){
    $.ajax({
      data: data,
      type: type,
      url: window.location.href,
      success: function(response){
        $('.message-div').html($(response).next('div.message-div'));
        //location.reload();
        $('#example-processing').css('display','none');
      },
      error: function(response){
        console.log(response);
      }
    });
    },500); 
  })
});
