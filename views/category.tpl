<!doctype html>
<html lang="en">
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>{{category['name']}} :: GIFless</title>

    <link href="/static/bootstrap.min.css" rel="stylesheet">
    <link href="/static/jumbotron.css" rel="stylesheet">
    <link href="/static/index.css" rel="stylesheet">
    <noscript><link href="/static/noindex.css" rel="stylesheet"></noscript>

    <script src="/static/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <!--<script>window.jQuery || document.write('<script src="https://getbootstrap.com/assets/js/vendor/jquery.min.js"><\/script>')</script>-->
    <script src="/static/popper.min.js"></script>
    <script src="/static/bootstrap.min.js"></script>
  </head>

  <body>

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
        <!--<form class="form-inline my-2 my-lg-0">
          <input class="form-control mr-sm-2" type="text" placeholder="Film Name" aria-label="Search">
          <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
        </form>-->
      </div>
    </nav>

    <main role="main">

      <!-- Main jumbotron for a primary marketing message or call to action -->
      <div class="jumbotron">
        <div class="container">
          <table>
            <tr>
              <td class="category-image">
                <div class="img-container"><img src="/{{category['image']}}" class="img-thumbnail"></div>
              </td>
              <td class="category-container">
                <h1 class="display-3 category-name text-resize" id="title">{{category['name']}}</h1>
                <p class="category-description" id="subtitle">{{category['description']}}</p>
              </td>
            </tr>
          </table>
        </div>
      </div>

      <div class="container">
        <div class="row">
          <div class="input-group input-group-lg fadeOut">
            <!--<span class="input-group-addon" id="sizing-addon1">@</span>-->
            <input type="text" id="quoteSearch" class="form-control" placeholder="Enter Quote" aria-label="Enter Quote" aria-describedby="sizing-addon1">
            <span class="input-group-btn">
              <button class="btn btn-primary" type="button">Search</button>
            </span>
          </div>
        </div>
        </br>
        </br>

        <div class="row">
          <table id="resultsTable" class="table table-hover fadeOut">
            <col width="5%">
            <col width="60%">
            <col width="20%">
            <col width="15%">
            <thead>
              <tr>
                <th scope="col">#</th>
                <th scope="col">Quote</th>
                <th scope="col">Release</th>
                <th scope="col">Time</th>
              </tr>
            </thead>
            <tbody id="tablecontents">

            </tbody>
          </table>
        </div>
        <hr>
      </div>
    </main>

    <script>var category = '{{category['reference']}}'</script>
    <script src="/static/quotesearch.js"></script>
  </body>
</html>
