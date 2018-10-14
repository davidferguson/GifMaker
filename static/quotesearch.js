var currentRequest = 0

function runSearch(category, query) {

  if (query.trim() == '' || category.trim() == '') {
    return
  }

  currentRequest = currentRequest + 1

  var url = '/search/' + encodeURIComponent(category) + '/' + encodeURIComponent(query) + '/' + currentRequest
  console.log(url)

  var request = new XMLHttpRequest()
  request.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var results = this.responseText
      results = JSON.parse(results)

      console.log(results.counter, currentRequest)
      if (results.counter != currentRequest) {
        return
      }

      console.log(results.counter == currentRequest)
      console.log(results.results.length)

      updateTable(results.results)
    }
  };

  request.open('GET', url, true)
  request.send()
}

function updateTable(results) {
  // quick hack, delete the table and add the new results in

  // delete everything
  var table = document.getElementById('tablecontents')
  while (table.hasChildNodes()) {
    table.removeChild(table.lastChild)
  }

  // add the new stuff in
  for (var i = 0; i < results.length; i++) {
    var result = results[i]

    var row = document.createElement('tr')
    row.setAttribute('onclick', 'selectQuote(' + result.id + ')')
    row.setAttribute('class', 'quoteResult fadeOut')

    var number = document.createElement('td')
    number.innerText = i + 1
    row.appendChild(number)

    var quote = document.createElement('td')
    quote.innerText = result.quote
    row.appendChild(quote)

    var ref = document.createElement('td')
    ref.innerText = result.media
    row.appendChild(ref)

    var time = document.createElement('td')
    time.innerText = result.start.split('.')[0]
    row.appendChild(time)

    table.appendChild(row)
  }
}

var input = document.getElementById('quoteSearch')
var oldInput

// do auto search after 200ms
/*input.addEventListener('input', function (evt) {
  oldInput = input.value
  setTimeout(function() {
    if (input.value == oldInput) {
      runSearch(category, document.getElementById('quoteSearch').value)
    }
  }, 1000)
})*/

input.addEventListener('input', function (evt) {
  searchInput()
})

//input.onkeydown = searchInput;

function searchInput() {
  var num = Math.floor(Math.random() * 20)
  var oldInput = input.value.toString()
  console.log(num, oldInput)
  setTimeout(function() {
    console.log(num, oldInput)
    if (input.value == oldInput) {
      runSearch(category, document.getElementById('quoteSearch').value)
    }
  }, 300)
}

input.onkeydown = function() {
  if (event.keyCode == 13) {
    //oldInput = oldInput + 'l' // anything to make it different
    runSearch(category, document.getElementById('quoteSearch').value)
  }
}


function selectQuote(quoteID) {
  // fade the table rows
  /*var rows = document.getElementsByClassName('quoteResult')
  for (var i = 0; i < rows.length; i++) {
    rows[i].style.opacity = 0
  }*/
  // fade out the table
  var table = document.getElementById('resultsTable')
  table.style.opacity = 0

  // also fade out the search box
  input.parentNode.style.opacity = 0

  // wait for the fade to complete, and then delete them
  setTimeout(function() {
    // delete the input field and table
    var tableContainer = document.getElementsByClassName('row')[1]
    tableContainer.parentNode.removeChild(tableContainer)
    var row1 = document.getElementsByClassName('row')[0]
    row1.removeChild(row1.children[0])

    // modify the title
    document.title = 'Generating GIF :: GIFless'

    // modify the page header
    var title = document.getElementById('title')
    var subtitle = document.getElementById('subtitle')
    title.innerText = 'Generating GIF'
    subtitle.innerText = 'Contacting media server...'

    // create the loading gif which will also be used for the final gif
    var img = document.createElement('img')
    img.setAttribute('class', 'img-fluid')
    img.id = 'gifImage'
    img.src = '/static/loading.gif'
    row1.appendChild(img)

    generateGif(quoteID)
  }, 300)
}

function generateGif(quoteID) {
  var websocket = new WebSocket("ws://" + window.location.hostname + ":8000/")

  websocket.onopen = function(evt) {
    // websocket is open, send the gif making request
    var data = {}
    data.quote = quoteID
    data.category = category
    data = JSON.stringify(data)

    websocket.send(data)
  }

  websocket.onmessage = function(evt) {
    var message = evt.data
    try {
      message = JSON.parse(message)
    } catch (e) {
      console.error('unable to parse JSON message')
      return
    }

    console.log(message)

    var action = message.action

    if (action == 'updateStatus') {
      var status = message.status
      document.getElementById('subtitle').innerText = status
      return
    }

    if (action == 'finished') {
      var imageUrl = message.url
      var image = document.getElementById('gifImage')
      image.src = imageUrl
    }
  }

  websocket.onerror = function(evt) {
    console.error('websocket error', evt.data)
  }
}
