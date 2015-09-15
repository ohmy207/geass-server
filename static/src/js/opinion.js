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
        isNoShowToTop: false,
        hasVoted: false,

        // render data
        render: function(re) {
            var opinionHtml = template('tmpl_opinion', re.data);
            jq('.warp').prepend(opinionHtml);

            jq('.warp, #bottomBar').show()
            //jq('.warp, #bottomBar, .recommendTitle').show()

            exports.hasVoted = re.data.has_user_voted || false;
        },

        init: function() {
            var tId = window.tId;
                loadOpts = {
                    isList: false,
                    isEmptyShow: false,
                    url: '/opinions/' + window.pId,
                    emptyCon: '',
                    callback: exports.render,
                };

            thread.load(loadOpts, 'drag');

            initLazyload('.warp img');

            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var thisObj = jq(this);
                thread.reply(tId, null, '', 'opinion');
            });

            jq('.warp').on('click', '.detail', function(e) {
                jq.UTIL.touchStateNow(jq(this), 'tapBg1');
                jq.UTIL.reload(jq(this).data('link'));
            });

            // vote
            jq('.warp').on('click', '.vote', function(e) {

                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    pId = thisObj.attr('pId') || null,
                    isVoted = thisObj.hasClass('voted'),
                    voteNum = parseInt(thisObj.data('num'));

                var callback = function() {
                    if(isVoted && exports.hasVoted) {
                        var opts = {
                            'id':'operationConfirm',
                            'isMask':true,
                            'content':'可以取消这次投票重新选择，确定要取消吗',
                            'okValue':'确定',
                            'cancelValue':'取消',
                            'ok':function() {
                                var opts = {
                                    'success': function(result) {
                                        if (result.code == 0) {
                                            exports.hasVoted = false;
                                            jq.UTIL.likeTips(thisObj, '-1');
                                            thisObj.attr('class', 'voteCount vote');
                                            thisObj.html(voteNum - 1);
                                            thisObj.data('num', voteNum - 1);
                                        }
                                    },
                                    'noShowLoading' : true,
                                    'noMsg' : true
                                }

                                var url = '/user/unvote/opinions';
                                var data = {'tid':tId, 'pid': pId};

                                jq.UTIL.ajax(url, data, opts);
                            },
                        };
                        jq.UTIL.dialog(opts);
                    } else if (!isVoted && !exports.hasVoted){
                        var opts = {
                            'success': function(result) {
                                if (result.code == 0) {
                                    exports.hasVoted = true;
                                    jq.UTIL.likeTips(thisObj, '+1');
                                    thisObj.attr('class', 'voteCount voted vote');
                                    thisObj.html(voteNum + 1);
                                    thisObj.data('num', voteNum + 1)
                                }
                            },
                            'noShowLoading' : true,
                            'noMsg' : true
                        }

                        var url = '/user/vote/opinions';
                        var data = {'tid':tId, 'pid': pId};

                        jq.UTIL.ajax(url, data, opts);
                    } else if (!isVoted && exports.hasVoted) {
                        var opts = {
                            'id':'operationConfirm',
                            'isMask':true,
                            'content':'要取消之前的投票重新选择吗?',
                            'okValue':'确定',
                            'cancelValue':'取消',
                            'ok':function() {
                                var opts = {
                                    'success': function(result) {
                                        if (result.code == 0) {
                                            var votedObj = jq('.voted');
                                            oldVoteNum = parseInt(votedObj.data('num'));
                                            votedObj.attr('class', 'voteCount vote');
                                            votedObj.html(oldVoteNum - 1);
                                            votedObj.data('num', oldVoteNum - 1);

                                            jq.UTIL.likeTips(thisObj, '+1');
                                            thisObj.attr('class', 'voteCount voted vote');
                                            thisObj.html(voteNum + 1);
                                            thisObj.data('num', voteNum + 1)
                                        }
                                    },
                                    'noShowLoading' : true,
                                    'noMsg' : true
                                }

                                var url = '/user/revote/opinions';
                                var data = {'tid':tId, 'pid': pId};

                                jq.UTIL.ajax(url, data, opts);
                            },
                        };
                        jq.UTIL.dialog(opts);

                    }
                };
                thread.checkIsRegistered(callback);
            });

        },

    };

    exports.init();

});
