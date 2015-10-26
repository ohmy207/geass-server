/**
 **/

require.config({

    waitSeconds: 15,
    urlArgs: "t=" + (new Date()).getTime(),

    paths: {

        //"jquery": "vendor/jquery-1.11.2.min",
        "jquery": "vendor/jquery.min",
        "art-template": "vendor/art-template",
        "util": "module/util",

        "jpegMeta": "module/jpegMeta",
        "JPEGEncoder": "module/JPEGEncoder",
        "imageCompresser": "module/imageCompresser",
        "uploadImg": "module/uploadImg",
        "thread": "module/thread",
    }

});

require(['art-template', 'util', 'thread'],function (template, util, thread){

    var exports = {
        //hasVoted: false,

        // render data
        render: function(re) {
            var opinionHtml = template('tmpl_opinion', re.data);
            jq('.warp').prepend(opinionHtml);

            jq('#bottomBar .iconReply').html(re.data.comments_count);
            jq('.warp, #bottomBar').show()
            //jq('.warp, #bottomBar, .recommendTitle').show()

            //exports.hasVoted = re.data.has_user_voted || false;
        },

        init: function() {
            var tId = window.tId,
                loadOpts = {
                    isList: false,
                    isEmptyShow: false,
                    url: '/opinions/' + window.oId,
                    emptyCon: '',
                    callback: exports.render,
                };

            thread.load(loadOpts, 'drag');
            initLazyload('.warp img');

            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var callback = function() {
                    thread.edit(loadOpts.url, 'opinion');
                };
                thread.checkIsRegistered(callback);
            });

            jq('.warp').on('click', '.threadPic img', function() {
                var thisObj = jq(this),
                    current = thisObj.data('src'),
                    urls = [];

                jq('.threadPic img').each(function() {
                    urls.push(jq(this).data('src'));
                });

                wx.previewImage({
                    current: current,
                    urls: urls
                });
            });

            jq('.warp').on('click', '.detail', function(e) {
                jq.UTIL.touchStateNow(jq(this), 'tapBg1');
                jq.UTIL.reload(jq(this).data('link'));
            });

            // approve
            jq('.warp').on('click', '.approve', function(e) {
                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    oId = thisObj.attr('oid') || null,
                    resultClass = "approve c13 f16",
                    resultNum = parseInt(thisObj.data('num')) + 1,
                    likeTips = "+1",
                    isAjaxDelete = false;

                var callback = function() {
                    if(thisObj.hasClass('c13')) {
                        resultClass = "approve c12 f16";
                        resultNum = parseInt(thisObj.data('num')) - 1;
                        likeTips = "-1";
                        isAjaxDelete = true;
                    }

                    var opts = {
                        'success': function(result) {
                            if (result.code == 0) {
                            //if (result.code == 0 && result.data && result.data.likeNum) {
                                thisObj.children('span').html(resultNum);
                                thisObj.attr('class', resultClass);
                                thisObj.data('num', resultNum);
                                jq.UTIL.likeTips(thisObj, likeTips);
                            }
                        },
                        'noShowLoading' : true,
                        'noMsg' : true
                    }

                    var url = '/user/approving/opinions/' + oId;
                    var data = {};

                    if (isAjaxDelete) {
                        jq.UTIL.ajax(url, data, opts, 'DELETE');
                    } else {
                        jq.UTIL.ajax(url, data, opts);
                    }
                };
                thread.checkIsRegistered(callback);
            });

        },

    };

    exports.init();

});
