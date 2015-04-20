
define(function() {

    var exports = {

        os: {},
        init: function(){
        
            exports.os.isiDevice = /ipad|iphone|ipod/i.test(navigator.userAgent.toLowerCase());
            exports.os.isAndroid = /android/i.test(navigator.userAgent.toLowerCase());
            exports.os.Version = '';
        },

        toast: function(msg){
            $("<div><h3>"+msg+"</h3></div>")
            .css({
                opacity: 0.90,
                display: "block",
                color: '#F0F0F0',
                position: "fixed",
                padding: "7px",
                width: "270px",

                'background-color': '#5B5B5B',
                "text-align": "center",
                'border-radius': '3px',
                '-webkit-box-shadow': '0px 0px 24px -1px rgba(56, 56, 56, 1)',
                '-moz-box-shadow': '0px 0px 24px -1px rgba(56, 56, 56, 1)',
                'box-shadow': '0px 0px 24px -1px rgba(56, 56, 56, 1)',

                left: ($(window).width() - 284)/2,
                top: $(window).height()/2
            })

            .appendTo($('body')).delay(1500)
            .fadeOut(400, function(){
                $(this).remove();
            });
        },

        createCORSRequest: function(method, url) {
          var xhr = new XMLHttpRequest();
          if ("withCredentials" in xhr) {

            // Check if the XMLHttpRequest object has a "withCredentials" property.
            // "withCredentials" only exists on XMLHTTPRequest2 objects.
            xhr.open(method, url, true);

          } else if (typeof XDomainRequest != "undefined") {

            // Otherwise, check if XDomainRequest.
            // XDomainRequest only exists in IE, and is IE's way of making CORS requests.
            xhr = new XDomainRequest();
            xhr.open(method, url);

          } else {

            // Otherwise, CORS is not supported by the browser.
            xhr = null;

          }
          return xhr;
        }

    }
    exports.init();

    return exports
});
