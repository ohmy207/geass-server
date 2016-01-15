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

        // render data
        render: function(re) {
            re.data.colorList = thread.colorList;
            var proposalHtml = template('tmpl_proposal', re.data);
            jq('.warp').prepend(proposalHtml);

            //jq('#bottomBar .iconReply').html(re.data.comments_count);
            jq('.warp, #bottomBar').show();
            //jq('.warp, #bottomBar, .recommendTitle').show()
            thread.voteTotalNum = re.data.vote_total_num || 0;
            thread.resetOpbar(jq('.opWrap'), thread.voteTotalNum, window.pos);

            exports.hasVoted = re.data.has_user_voted || false;
            thread.initWeixin({
                title: re.data.proposal.title + ' - ' + re.data.proposal.topic_title,
                desc: re.data.proposal.content,
                imgUrl: re.data.proposal.picture_urls.length > 0 ? re.data.proposal.picture_urls[0]['origin'] : '',
            });
        },

        init: function() {
            var tId = window.tId;
                loadOpts = {
                    isList: false,
                    isEmptyShow: false,
                    url: '/proposals/' + window.pId,
                    emptyCon: '',
                    callback: exports.render,
                };

            thread.load(loadOpts, 'drag');
            initLazyload('.warp img');

            jq('.warp, #bottomBar').on('click', '.threadEdit', function() {
                var callback = function() {
                    thread.edit(loadOpts.url, 'proposal');
                };
                thread.checkIsRegistered(callback);
            });

            jq('.warp').on('click', '.threadPic img', function() {
                var thisObj = jq(this),
                    current = thisObj.data('origin'),
                    urls = [];

                jq('.threadPic img').each(function() {
                    urls.push(jq(this).data('origin'));
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

            // vote
            jq('.warp').on('click', '.vote', function(e) {

                jq.UTIL.touchStateNow(jq(this));
                e.stopPropagation();

                var thisObj = jq(this),
                    pId = thisObj.attr('pId') || null,
                    isVoted = thisObj.hasClass('voted'),
                    resultNum = parseInt(thisObj.data('num')) + 1,
                    resultClass = "voteCount voted vote",
                    resultStyle = {'background': thisObj.nextAll('.oppi').css('color')},
                    //likeTips = "+1",
                    hasVoted = true,
                    url = '/user/voting/proposals/' + pId,
                    ajaxType = 'POST',
                    data = {},
                    voteTotalNum = thread.voteTotalNum + 1;

                var callback = function() {
                    if(isVoted && exports.hasVoted) {
                        resultNum = parseInt(thisObj.data('num')) - 1;
                        resultClass = "voteCount vote";
                        resultStyle = {'background': ''};
                        //likeTips = "-1";
                        hasVoted = false;
                        ajaxType = 'DELETE';
                        voteTotalNum = thread.voteTotalNum - 1;
                    }

                    var opts = {
                        'success': function(result) {
                            if (result.code == 0) {
                                exports.hasVoted = hasVoted;
                                //jq.UTIL.likeTips(thisObj, likeTips);
                                thisObj.attr('class', resultClass);
                                thisObj.css(resultStyle);
                                thisObj.html(resultNum);
                                thisObj.data('num', resultNum);
                                thread.voteTotalNum = voteTotalNum;
                                thread.resetOpbar(jq('.opWrap'), thread.voteTotalNum, window.pos);
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
                                        votedObj.css({'background': ''});
                                        votedObj.html(oldVoteNum - 1);
                                        votedObj.data('num', oldVoteNum - 1);

                                        //jq.UTIL.likeTips(thisObj, likeTips);
                                        thisObj.attr('class', resultClass);
                                        thisObj.css(resultStyle);
                                        thisObj.html(resultNum);
                                        thisObj.data('num', resultNum);

                                        thread.resetOpbar(jq('.opWrap'), thread.voteTotalNum, window.pos);
                                    }
                                },

                                jq.UTIL.ajax(url, data, opts, 'PATCH');
                            },
                        };
                        jq.UTIL.dialog(dialogOpts);

                    } else {
                        jq.UTIL.ajax(url, data, opts, ajaxType);
                    }
                };
                thread.checkIsRegistered(callback);
            });

        },

    };

    exports.init();

});
