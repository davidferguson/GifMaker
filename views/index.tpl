<!doctype html>
<html lang="en">
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>GIFless</title>

    <link href="/static/bootstrap.min.css" rel="stylesheet">
    <link href="/static/jumbotron.css" rel="stylesheet">
    <link href="/static/index.css" rel="stylesheet">
    <noscript><link href="/static/noscript.css" rel="stylesheet"></noscript>
    <style>
      ::-webkit-input-placeholder {
        font-style: italic;
      }
      :-moz-placeholder {
        font-style: italic;
      }
      ::-moz-placeholder {
        font-style: italic;
      }
      :-ms-input-placeholder {
        font-style: italic;
      }
    </style>

    <script src="/static/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <!--<script>window.jQuery || document.write('<script src="https://getbootstrap.com/assets/js/vendor/jquery.min.js"><\/script>')</script>-->
    <script src="/static/popper.min.js"></script>
    <script src="/static/bootstrap.min.js"></script>
    <script src="/static/index.js"></script>
  </head>

  <body onload="pageLoaded()">

    <nav class="navbar navbar-expand-md navbar-dark fixed-top bg-dark">
      <a class="navbar-brand" href="/">GIFless</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarsExampleDefault" aria-controls="navbarsExampleDefault" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarsExampleDefault">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item">
            <a class="nav-link" href="/static/about.html">About</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/static/contact.html">Contact</a>
          </li>
        </ul>
        <form class="form-inline my-2 my-lg-0">
          <input class="form-control mr-sm-2" type="text" placeholder="Film Name" aria-label="Search">
          <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
        </form>
      </div>
    </nav>

    <main role="main">

      <!-- Main jumbotron for a primary marketing message or call to action -->
      <div class="jumbotron">
        <div class="container">
          <h1 class="display-3">GIFless</h1>
          <p>Select a film, TV show or franchise, enter your favourite quote, and leave with a newly created GIF!</p>
          <p><a class="btn btn-primary btn-lg" href="#" role="button">Learn more &raquo;</a></p>
        </div>
      </div>

      <div class="container">
        % for film in films:
          % if film['index'] % 3 == 0:
            <div class="row">
          % end
          <div id="film{{film['index']}}" class="col-md-4 film" data-category="{{film['category']}}" onclick="filmChosen({{film['index']}})">
            <noscript>
              <a href=""><h2 class="film-name">{{film['name']}}</h2></a>
            </noscript>
            <script>
              document.write('<h2 class="film-name">{{film['name']}}</h2>')
            </script>
            <div class="img-container"><img src="/{{film['image']}}" class="img-thumbnail" onload="return;setTimeout(function(){$('#film{{film['index']}}').css({opacity: 1,transform: 'scale(1, 1)'})},1);$('#film{{film['index']}}').removeClass('unloaded')"></div>
            <div class="description-container"><p class="film-description">{{film['description']}}</p></div>
          </div>

          % if film['index'] % 3 == 2:
            </div>
          % end
        % end

        <hr>
      </div>
    </main>
  </body>
</html>
