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
                url: '/topics/' + window.tId + '/proposals',
                emptyCon: '还没有选项',
                callback: exports.renderList,
            }, action);
        },

        // render data
        renderList: function(re) {
            thread.voteTotalNum = re.data.vote_total_num || 0;
            exports.hasVoted = re.data.has_user_voted || false;

            var proposalsHtml = template('tmpl_proposals', re.data);
            if(jq.trim(proposalsHtml)!==''){
                jq('#hotReplyList').append(proposalsHtml);
                thread.resetAllOpbar();
            }
        },

        init: function() {

            exports.load('drag');
            initLazyload('.warp img');
            thread.initTouchRefresh(exports.load);

            jq('.warp').on('click', '.proposalWrap', function(e) {
                var thisObj = jq(this), link;
                jq.UTIL.touchStateNow(thisObj.parent('li'));

                link = thisObj.data('link') || '';
                if (link) {
                    jq.UTIL.reload(link);
                }
                return false;
            });

            // vote
            jq('#hotReplyList').on('click', '.vote', function(e) {

                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    pId = thisObj.attr('pId') || null,
                    isVoted = thisObj.hasClass('voted'),
                    resultNum = parseInt(thisObj.data('num')) + 1,
                    resultClass = "voteCount voted vote",
                    //likeTips = "+1",
                    hasVoted = true,
                    url = '/user/vote/proposals',
                    data = {'tid':tId, 'pid': pId},
                    voteTotalNum = thread.voteTotalNum + 1;

                var callback = function() {
                    if(isVoted && exports.hasVoted) {
                        resultNum = parseInt(thisObj.data('num')) - 1;
                        resultClass = "voteCount vote";
                        //likeTips = "-1";
                        hasVoted = false;
                        url = '/user/unvote/proposals';
                        voteTotalNum = thread.voteTotalNum - 1;
                    }

                    var opts = {
                        'success': function(result) {
                            if (result.code == 0) {
                                exports.hasVoted = hasVoted;
                                //jq.UTIL.likeTips(thisObj, likeTips);
                                thisObj.attr('class', resultClass);
                                thisObj.html(resultNum);
                                thisObj.data('num', resultNum);
                                thread.voteTotalNum = voteTotalNum;
                                thread.resetAllOpbar();
                            }
                        },
                        'noShowLoading' : true,
                        'noMsg' : true
                    }

                    if (!isVoted && exports.hasVoted) {
                        var dialogOpts = {
                            'id':'operationConfirm',
                            'isMask':true,
                            'content':'要取消之前的投票重新选择吗?',
                            'okValue':'确定',
                            'cancelValue':'取消',
                            'ok':function() {
                                opts.success = function(result) {
                                    if (result.code == 0) {
                                        var votedObj = jq('.voted');
                                        oldVoteNum = parseInt(votedObj.data('num'));
                                        votedObj.attr('class', 'voteCount vote');
                                        votedObj.html(oldVoteNum - 1);
                                        votedObj.data('num', oldVoteNum - 1);

                                        //jq.UTIL.likeTips(thisObj, likeTips);
                                        thisObj.attr('class', resultClass);
                                        thisObj.html(resultNum);
                                        thisObj.data('num', resultNum);

                                        thread.resetAllOpbar();
                                    }
                                },

                                url = '/user/revote/proposals';
                                jq.UTIL.ajax(url, data, opts);
                            },
                        };
                        jq.UTIL.dialog(dialogOpts);

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
