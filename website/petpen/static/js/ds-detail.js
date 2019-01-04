$(function(){
  document.querySelector('#overview').addEventListener('load',removeLoadingClass);
  $('input[type=radio][name=type]').change(function(){
    var url = 'view/?type='+this.value;
    $('.loading').show();
    $('.p-info').hide();
    $('#overview').attr('src',url);
  });
});
function showOverview(url){
  $('#overview').attr(src,url);
};
function removeLoadingClass(){
  $('.loading').hide();
};
