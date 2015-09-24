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
        hasVoted: false,

        load: function(action) {
            thread.load({
                isList: true,
                isEmptyShow: true,
                url: '/topics/' + window.tId + '/comments' + '?pid=' + window.pId,
                emptyCon: '还没有任何评论',
                callback: exports.renderList,
            }, action);
        },

        // render data
        render: function(re) {
            var opinionHtml = template('tmpl_opinion', re.data);
            jq('.warp').prepend(opinionHtml);

            //jq('#bottomBar .iconReply').html(re.data.comments_count);
            jq('.warp, #bottomBar').show()
            //jq('.warp, #bottomBar, .recommendTitle').show()

            exports.hasVoted = re.data.has_user_voted || false;
        },

        renderList: function(re) {
            var allReplyHtml = template('tmpl_reply', re.data);
            if(jq.trim(allReplyHtml)!==''){
                //jq('#allLabelBox').show();
                jq('#allReplyList').css({height:'auto'})
                jq('#allReplyList').append(allReplyHtml);
            }
        },

        init: function() {
            var tId = window.tId;
                loadOpts = {
                    isList: false,
                    isEmptyShow: true,
                    url: '/opinions/' + window.pId,
                    emptyCon: '还没有任何评论',
                    callback: exports.render,
                };

            thread.load(loadOpts, 'drag');

            initLazyload('.warp img');

            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var thisObj = jq(this),
                    callback = function() {
                        thread.reply(tId, pId,  null, '', 'comment');
                    };
                thread.checkIsRegistered(callback);
            });

            jq('.warp').on('click', '.commReply', function(e) {
                var thisObj = jq(this);
                if (thisObj.hasClass('unfold')) {
                    thisObj.attr('class', 'commReply');
                } else {
                    thisObj.attr('class', 'commReply unfold');
                }
            });

            // 回复
            jq('.warp').on('click', '.replyFloor', function(e) {
                var thisObj = jq(this).parents('li');
                //var authorUId = thisObj.attr('uid');
                // 获取帖子id
                var divId = thisObj.attr('id'), author;

                var callback = function() {
                    if (/co_[0-9a-f]{24}/.test(divId)) {
                        if (match = divId.match(/co_([0-9a-f]{24})/)) {
                            toCoId = match[1];
                        }

                        e.stopPropagation();
                        jq.UTIL.touchStateNow(jq(this));

                        author = thisObj.attr('author');
                        thread.reply(tId, pId, toCoId, author, 'comment');
                    }
                };
                thread.checkIsRegistered(callback);
            });

            thread.initTouchRefresh(exports.load);

            jq('.warp').on('click', '.detail', function(e) {
                jq.UTIL.touchStateNow(jq(this), 'tapBg1');
                jq.UTIL.reload(jq(this).data('link'));
            });

            // like
            jq('.warp').on('click', '.like', function(e) {
                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    coId = thisObj.attr('coid') || null;

                var callback = function() {
                    if(thisObj.children('i').hasClass('iconPraise')) {
                        return;
                    }

                    var opts = {
                        'success': function(result) {
                            if (result.code == 0) {
                            //if (result.code == 0 && result.data && result.data.likeNum) {
                                jq.UTIL.likeTips(thisObj, '+1');
                                thisObj.html('<i class="iconPraise f18 cf"></i>' + (parseInt(thisObj.data('num')) + 1));
                            }
                        },
                        'noShowLoading' : true,
                        'noMsg' : true
                    }

                    var url = '/user/like/comments';
                    var data = {'tid':tId, 'coid': coId};

                    jq.UTIL.ajax(url, data, opts);
                };
                thread.checkIsRegistered(callback);
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
