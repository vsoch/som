/*** BEGIN FILE EXPLORER CODE ***/
//Show and Hide the image preloader so expanded content is not seen by the user.
$('.menu-tree-preloader').hide();
$('.menu-tree').show();

// Execute this after the site is loaded.
$(function() {
    // Find list items representing folders and
    // style them accordingly.  Also, turn them
    // into links that can expand/collapse the
    // tree leaf.
    $('.menu-tree li > ul').each(function(i) {
        // Find this list's parent list item.
        var parent_li = $(this).parent('li');

        // Temporarily remove the list from the
        // parent list item, wrap the remaining
        // text in an anchor, then reattach it.
        var sub_ul = $(this).remove();
        parent_li.wrapInner('<a/>').find('a').click(function() {
            // Make the anchor toggle the leaf display.
            sub_ul.slideToggle(300);
          
          //Add class to change folder image when clicked on
          $(this).toggleClass('expanded');
          
        });
        parent_li.append(sub_ul);
    });

    // Hide all lists except the outermost.
    $('.menu-tree ul ul').hide();
});

/*** END FILE EXPLORER CODE ***/
