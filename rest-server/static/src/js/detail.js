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
        isLoadingFirst: true,

        load: function(action) {
            var url = '/topics/' + window.tId,
                isLoadingFirst = exports.isLoadingFirst;

            thread.load({
                isList: !isLoadingFirst,
                isEmptyShow: true,
                url: isLoadingFirst ? url : url + '/opinions',
                emptyCon: '还没有看法哦！',
                callback: isLoadingFirst ? exports.render : exports.renderList,
            }, action);
        },

        // render data
        render: function(re) {
            var topicHtml = template('tmpl_topic', re.data);
                is_topic_followed = re.data.is_topic_followed || false;
            jq('.detailBox').prepend(topicHtml);

            var follow_class = is_topic_followed ? 'item cf iconFollow' : 'item cf iconNoFollow';
                follow_html = is_topic_followed ? '已关注' : '关注';
            jq('#bottomBar #follow').attr('class', follow_class).html(follow_html);
            jq('#bottomBar .iconReply').html(re.data.comments_count);

            window.isLZ = re.data.is_lz || false;
            window.vote_total_num = re.data.vote_total_num || 0;
            window.color_list = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#bcbd22', '#17becf', '#aec7e8'];
            exports.hasVoted = re.data.has_user_voted || false;

            var ReplyHtml = template('tmpl_proposals', {
                'data_list': re.data.proposal_list,
                'vote_total_num': vote_total_num,
                'color_list': window.color_list,
            });

            if(jq.trim(ReplyHtml)!==''){
                //jq('#allLabelBox').show();
                jq('#hotReplyList').append(ReplyHtml);
                jq('#hotReplyList').css({height:'auto'})
            } else {
                jq('#emptyProposals').show();
            }

            exports.renderList(re)

            jq('.warp, #bottomBar, .recommendTitle').show();

            exports.isLoadingFirst = false;
        },

        renderList: function(re) {
            var ReplyHtml = template('tmpl_opinions', re.data);
            if(jq.trim(ReplyHtml)!==''){
                //jq('#hotLabelBox').show();
                jq('#allReplyList').css({height:'auto'})
                jq('#allReplyList').append(ReplyHtml);
            }
        },

        init: function() {
            var tId = window.tId;

            // 分享遮罩，一次性
            //var action = jq.UTIL.getQuery('action');
            //var reapp = /qqdownloader\/([^\s]+)/i;

            exports.load('drag');

            initLazyload('.warp img');
            initLazyload('#opinionList img');

            // appbar no share mask
            //if (action == 'share' && !reapp.test(navigator.userAgent)) {
            //    var hadShowShareMask = localStorage.getItem('hadShowShareMask'),
            //        isMask = false;
            //    if (!hadShowShareMask) {
            //        isMask = true;
            //    }
            //    var tmpl = template.render('tmpl_pageTip', {'msg':'喜欢这个话题，请点击右上角图标分享'});
            //    jq.UTIL.dialog({
            //        id: 'shareMask',
            //        top:0,
            //        content: tmpl,
            //        isHtml: true,
            //        isMask: isMask,
            //        callback: function() {
            //            jq('.gMask').on('click', function() {
            //                jq.UTIL.dialog({id:'shareMask'});
            //            });
            //            jq('#showShare').on('click', function() {
            //                jq(this).hide();
            //            });
            //        }
            //    });
            //    localStorage.setItem('hadShowShareMask', 1);
            //}

            // 点击查看大图
            //require.async('module/imageviewCommon', function(imageviewCommon) {
            //    imageviewCommon.init('.slideShow li');
            //    imageviewCommon.init('.threadPic span');
            //    imageviewCommon.init('.replyImg dd');
            //    // imageviewCommon.init('.slideBox li');
            //});

            //setInterval(function() {
            //    if (window.pageYOffset > 1000 && !thread.isNoShowToTop) {
            //        jq('#goTop').show();
            //    } else {
            //        jq('#goTop').hide();
            //    }

            //}, 200);

            //jq('.upBtn').on('click', function() {
            //    jq('#goTop').hide();
            //    scroll(0,0);
            //});

            // 主题和底部bar 帖点击回复
            jq('.warp, #bottomBar').on('click', '.threadReply', function() {
                var thisObj = jq(this),
                    callback = function() {
                        var replyType = thisObj.data('type');
                        thread.reply(tId, null, null, '', replyType);
                    };
                //jq.UTIL.touchStateNow(thisObj.parent('.topicTit'));
                thread.checkIsRegistered(callback);
            });

            thread.initTouchRefresh(exports.load);

            jq('#hotReplyList,#allReplyList').on('click', '.proposalWrap, .opinionWrap', function(e) {
                var thisObj = jq(this), link;
                jq.UTIL.touchStateNow(thisObj.parent('li'));

                link = thisObj.attr('data-link') || '';
                if (link) {
                    jq.UTIL.reload(link);
                }
                return false;
            });

            // follow
            jq('#bottomBar').on('click', '#follow', function(e) {

                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    tId = window.tId || null,
                    isFollowed = thisObj.hasClass('iconFollow');

                var opts = {
                    'noShowLoading' : true,
                    'noMsg' : true
                };

                var url = '/user/following/topics',
                    data = {'tid':tId};

                var callback = function() {
                    if (isFollowed) {
                        opts.success = function(result) {
                            if (result.code == 0) {
                                thisObj.attr('class', 'item cf iconNoFollow');
                                thisObj.html('关注')
                            }
                        };

                        jq.UTIL.ajax(url, data, opts, 'DELETE');
                    } else {
                        opts.success = function(result) {
                            if (result.code == 0) {
                                thisObj.attr('class', 'item cf iconFollow');
                                thisObj.html('已关注')
                            }
                        };
                        jq.UTIL.ajax(url, data, opts);
                    }
                };
                thread.checkIsRegistered(callback);
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
                    likeTips = "+1",
                    hasVoted = true,
                    url = '/user/vote/proposals',
                    data = {'tid':tId, 'pid': pId};

                var callback = function() {
                    if(isVoted && exports.hasVoted) {
                        resultNum = parseInt(thisObj.data('num')) - 1;
                        resultClass = "voteCount vote";
                        likeTips = "-1";
                        hasVoted = false;
                        url = '/user/unvote/proposals';
                    }

                    var opts = {
                        'success': function(result) {
                            if (result.code == 0) {
                                exports.hasVoted = hasVoted;
                                jq.UTIL.likeTips(thisObj, likeTips);
                                thisObj.attr('class', resultClass);
                                thisObj.html(resultNum);
                                thisObj.data('num', resultNum);
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

                                        jq.UTIL.likeTips(thisObj, likeTips);
                                        thisObj.attr('class', resultClass);
                                        thisObj.html(resultNum);
                                        thisObj.data('num', resultNum);
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
