var viewModel = {
    videos: new ko.observableArray([]),
    addVideo: function(video){
        viewModel.videos.push(video);
        viewModel.videos.valueHasMutated();
    }
}


//chargement de swfobject à partir du CDN de google
    google.load("swfobject", "2.1");

    // Update a particular HTML element with a new value
    function updateHTML(elmId, value) {
      document.getElementById(elmId).innerHTML = value;
    }

    // chargement de la vidéo concerné dans le player
    function loadVideoById(idvid) {
      var videoID = idvid;
      if(ytplayer) {
        ytplayer.loadVideoById(videoID);
      }
    }

    // fonction appellé en cas d'erreur
    function onPlayerError(errorCode) {
      alert("An error occured of type:" + errorCode);
    }

    // fonction appellé au chargement du player
    function onYouTubePlayerReady(playerId) {
      ytplayer = document.getElementById("ytPlayer");
      ytplayer.addEventListener("onError", "onPlayerError");
    }


    function loadPlayer() {
      var videoID = 'TYk6LenOnG4';
      var params = { allowScriptAccess: "always" };
      var atts = { id: "ytPlayer", wmode:"transparent" };

      swfobject.embedSWF("http://www.youtube.com/v/" + videoID + "&enablejsapi=1&playerapiid=player1",
            "videoDiv",
            440,
            240,
            "8", null, null, params, atts);
    }
    function _run() {
      loadPlayer();
    }


$(document).ready(function(){
    $.get("https://gdata.youtube.com/feeds/api/users/Datawinners/uploads", {'alt':"json"},
            function(data){
                var videos = JSON.parse(data);
                for(i in videos.feed.entry){
                    var url = videos.feed.entry[i].id.$t;
                    var id = url.substring(42);
                    video = {
                        id: id,
                        loadVideo: function(){ loadVideoById(id)},
                        src: "http://img.youtube.com/vi/"+id+"/0.jpg"
                    }
                    viewModel.addVideo(video);
                }
            }
    );

    
    google.setOnLoadCallback(_run);
    ko.applyBindings(viewModel);
})

