function generateGif(quoteID) {
  websocket = new WebSocket("ws://" + window.location.hostname + "/")

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

    var action = message.action

    if (action == 'updateStatus') {
      var status = message.status
      document.getElementById('status').innerText = status
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

//websocket.onclose = function(evt) { onClose(evt) }
