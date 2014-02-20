$(function(){
    $('#accordion').accordion({
        heightStyle: 'content',
        collapsible: true,
        active: false
    });
    $('#accordion>div[src]').each(function(){
        $(this).find('pre').load($(this).attr('src'));
    });
});
