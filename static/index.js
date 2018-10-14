function pageLoaded() {
  $( '.film-name' ).each(function ( i, box ) {

      var width = $( box ).width(),
          html = '<span style="white-space:nowrap">',
          line = $( box ).wrapInner( html ).children()[ 0 ],
          n = 32;

      $( box ).css( 'font-size', n );

      while ( $( line ).width() > width ) {
          $( box ).css( 'font-size', --n );
      }

      $( box ).text( $( line ).text() );

  });

  fadeFilm(0)
}

function imgLoaded(img) {
  return img.complete && img.naturalHeight !== 0;
}

function waitForImageLoad(img, cb) {
  if (img.complete && img.naturalHeight !== 0) {
    cb()
    return
  }

  setTimeout(function() {
    waitForImageLoad(img, cb)
  }, 5)
}

//function fadeFilm(index, opacity, direction, speed, leaveFilm) {
function fadeFilm(index) {
  var id = 'film' + index.toString()
  var film = document.getElementById(id)

  if (film == null) {
    return
  }

  // wait until my image has loaded
  var img = film.getElementsByTagName('img')[0]
  waitForImageLoad(img, function() {
    $('#' + id).css({opacity: 1, transform: 'scale(1, 1)'})
    $('#' + id).removeClass('unloaded')

    // do the next one
    setTimeout(function() {
      index = index + 1
      fadeFilm(index)
    }, 10)
  })
}

function hideFilm(index, startId, selectedId) {
  console.log(index, startId)
  if (index < startId) {
    return
  }

  var id = 'film' + index.toString()
  var film = document.getElementById(id)

  if (index != selectedId) {
    //$('#' + id).css({opacity: 0, transform: 'scale(1, 1)'})
    $('#' + id).css({display: 'none', transform: 'scale(1, 1)'})
  }

  // see if we can hide the parent now
  var parent = film.parentNode
  var films = parent.children
  var hide = true
  for (var i = 0; i < films.length; i++) {
    console.log(films[i].style.display)
    if (films[i].style.display != 'none') {
      hide = false
    }
  }
  if (hide) {
    parent.style.display = 'none'
  }

  // do the next one
  setTimeout(function() {
    index = index - 1
    hideFilm(index, startId, selectedId)
  }, 50)
}

function filmChosen(id) {
  // want entire disolve to take 1 second
  var maxId = document.getElementsByClassName('film').length

  //var chosen = document.getElementById('film' + id.toString())
  //var chosenParent = chosen.parentNode

  for (var i = 0; i < maxId; i++) {
    var film = document.getElementById('film' + i.toString())
    //var parent = film.parentNode

    film.style.opacity = 0
    film.style.visibility = 'hidden'
  }

  setTimeout(function() {
    var category = document.getElementById('film' + id.toString()).getAttribute('data-category')
    location.href = '/category/' + category
  }, 300)

  return

  /*var speed = 1000 / maxId
  if (speed > 50) {
    speed = 50
  }*/

  // fade out the films - only fade the ones in view
  var startId = id - 10
  var endId = id + 10

  /*if (startId < 0) {
    startId = 0
  }

  if (endId >= document.getElementsByClassName('film').length) {
    endId = document.getElementsByClassName('film').length - 1
  }*/

  startdId = id
  endId = id

  console.log(endId)
  console.log(startId)
  console.log(id)
  //hideFilm(endId, startId, id)

  for (var i = 0; i < startId; i++) {
    document.getElementById('film' + i.toString()).style.display = 'none'
  }

  for (var i = endId + 1; i < document.getElementsByClassName('film').length; i++) {
    document.getElementById('film' + i.toString()).style.display = 'none'
  }
}
