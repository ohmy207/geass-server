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

        load: function(action) {
            var pId = window.pId || null;
            var url_suffix = pId ? '?pid=' + pId : '';

            thread.load({
                isList: true,
                isEmptyShow: true,
                url: '/topics/' + window.tId + '/comments' + url_suffix,
                emptyCon: '还没有任何评论',
                callback: exports.renderList,
            }, action);
        },

        // render data
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
            var pId = window.pId || null;

            exports.load('drag');

            initLazyload('.warp img');

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
                        thread.reply(tId, pId,  null, '', 'comment');
                    };
                thread.checkIsRegistered(callback);
            });

            jq('#allReplyList').on('click', '.commReply', function(e) {
                var thisObj = jq(this);
                if (thisObj.hasClass('unfold')) {
                    thisObj.attr('class', 'commReply');
                } else {
                    thisObj.attr('class', 'commReply unfold');
                }
            });

            // 回复
            jq('#allReplyList').on('click', '.replyFloor', function(e) {
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

            // like
            jq('.topicCon .replyShare,#hotReplyList,#allReplyList').on('click', '.like', function(e) {
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

            /**
             * @desc 全部回复加倒序查看
             * @param desc 为0是正序，为1时倒序
             */
            //var replySortBtn = jq('.evtReplySort'),
            //    replySortIcon = replySortBtn.find('i'),
            //    replySortSwitch = function () {
            //        if (!exports.desc) {
            //            replySortIcon.removeClass('iconSequence');
            //            replySortIcon.addClass('iconReverse');
            //            replySortBtn.html('倒序排列');
            //            replySortBtn.prepend(replySortIcon);
            //        } else {
            //            replySortIcon.removeClass('iconReverse');
            //            replySortIcon.addClass('iconSequence');
            //            replySortBtn.html('正序排列');
            //            replySortBtn.prepend(replySortIcon);
            //        }
            //    };
            //replySortSwitch();
            //replySortBtn.on('click', function () {
            //    var allReplyWrap = jq('#allReplyList'),
            //        allReplyHeight = allReplyWrap.height();
            //    allReplyWrap.css({height: allReplyHeight});
            //    allReplyWrap.html('');
            //    exports.nextStart = 0;
            //    exports.desc = !exports.desc ? 1 : 0;
            //    replySortSwitch();
            //    exports.load(exports.nextStart, 'sort');
            //    //pgvSendClick({hottag: 'wsq.reply.sort.inverse'});
            //});

        },

    };

    exports.init();

});
