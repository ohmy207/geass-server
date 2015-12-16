/**
 **/

require.config({

    waitSeconds: 15,
    urlArgs: "t=" + (new Date()).getTime(),

    paths: {

        "jquery": "vendor/jquery-1.11.2.min",
        "jqueryForm": "vendor/jquery.form.min",
        "util": "module/util",

        "jpegMeta": "module/jpegMeta",
        "JPEGEncoder": "module/JPEGEncoder",
        "imageCompresser": "module/imageCompresser",
        "uploadImg": "module/uploadImg",

    }

});

require(['uploadImg', 'util'],function (uploadImg, util){

    //jq.UTIL.dialog({content:navigator.userAgent.toLowerCase(),autoClose:true});

    var exports = {

        contentHeight: 0,
        uploadTimer: null,

        // 上传相关
        initUpload: function() {
            // 上传图片的绑定
            // jq('#addPic').on('click', function() {
                // console.log(1);
            // });
            jq('#addPic').on('click', function() {
                if(!uploadImg.checkUploadBySysVer()){
                    return false;
                }
            });

            jq('#uploadFile, #fistUploadFile').on('click', function() {
                var thisObj = jq(this);
                if(jq('.photoList').find('#livideo').length > 0){
                    jq.UTIL.dialog({id: 'addWsTips', content: '图片和微视只能发一种哦~', autoClose: 2000});
                    return false;
                }
                if (uploadImg.isBusy) {
                    jq.UTIL.dialog({content:'上传中，请稍后添加', autoClose:true});
                    return false;
                }
                if(thisObj.attr('id') == 'fistUploadFile'){
                    if(jq('.iconSendImg').hasClass('fail')){
                        jq.UTIL.dialog({content:'不能再上传了，最多只能上传8张图片哦~', autoClose:true});
                        return false;
                    }
                }
            });

            jq('body').on('click', '.iconSendImg, .iconArrowR', function(e){
                var thisObj = jq(this);
                var photoList = jq('.photoList');
                //点击图片图标
                if(thisObj.hasClass('iconSendImg')){
                    if(photoList.is(':hidden')){
                        //jq('.sendCon').animate({height: '60'}, 300);
                        jq('.sendCon').css('height', '60');
                        photoList.show();
                    }
                }
                //查看更多表情
                if(thisObj.hasClass('iconArrowR')){
                    var expressionMenu = jq('.expressionMenu').find('a');
                    var haveMenuWidth = expressionMenu.length*76;
                    var expressionTabWidth = jq('.expressionTab').width();
                    if(haveMenuWidth > expressionTabWidth){
                        var firstChild = jq(expressionMenu[0]);
                        jq('.expressionMenu').append(firstChild.clone());
                        firstChild.remove();
                    }else{
                        jq.UTIL.dialog({id:'haveMoreExpression', content:'没有更多表情了哦~',autoClose:true});
                    }
                }

            });
            //首次点击图片的图标，触发一次手机的默认上传事件
            jq('body').on('change', '#fistUploadFile', function(e){
                var content = jq('#content')[0];
                jq('.photoList').show();
                jq('.operatList').hide();
                jq('.photoTipsBox').show();
                jq('.operatIcon').removeClass('on');
                jq('.iconSendImg').addClass('on');
                //jq('.sendCon').css('height', 'auto');
                //if(jq('.sendCon').height() != 60){
                //    //jq('.sendCon').animate({height: '60'}, 300);
                //    jq('.sendCon').css('height', '60');

                //}
                //传图时输入框定位到底部
                content.scrollTop = content.scrollHeight
            });

            // 文件表单发生变化时
            jq('body').on('change', '#uploadFile, #fistUploadFile', function(e) {
                //执行图片预览、压缩定时器
                uploadTimer = setInterval(function() {
                    // 预览
                    setTimeout(function() {
                        if (uploadImg.previewQueue.length) {
                            var jobId = uploadImg.previewQueue.shift();
                            uploadImg.uploadPreview(jobId);
                        }
                    }, 1);
                    // 上传
                    setTimeout(function() {
                        if (!uploadImg.isBusy && uploadImg.uploadQueue.length) {
                            var jobId = uploadImg.uploadQueue.shift();
                            uploadImg.isBusy = true;
                            uploadImg.createUpload(jobId, 'newthread', uploadTimer);
                            jq('#li'+jobId+' .cBtn').show();
                        }
                    }, 10);
                }, 300);

                e = e || window.event;
                var fileList = e.target.files;
                if (!fileList.length) {
                    return false;
                }

                for (var i = 0; i<fileList.length; i++) {
                    if (uploadImg.countUpload() >= uploadImg.maxUpload) {
                        jq.UTIL.dialog({content:'最多只能上传8张图片',autoClose:true});
                        break;
                    }

                    var file = fileList[i];

                    if (!uploadImg.checkPicType(file)) {
                        jq.UTIL.dialog({content: '上传照片格式不支持',autoClose:true});
                        continue;
                    }
                    // console.log(file);
                    if (!uploadImg.checkPicSize(file)) {
                        jq.UTIL.dialog({content: '图片体积过大', autoClose:true});
                        continue;
                    }

                    var id = Date.now() + i;
                    // 增加到上传对象中, 上传完成后，修改为 true
                    uploadImg.uploadInfo[id] = {
                        file: file,
                        isDone: false,
                    };

                    var html = '<li id="li' + id + '"><div class="photoCut"><img src="/static/img/defaultImg.png" class="attchImg" alt="photo"></div>' +
                            '<div class="maskLay"></div>' +
                            '<a href="javascript:;" class="cBtn cBtnOn pa db" style="display:none;" title="" _id="'+id+'">关闭</a></li>';
                    jq('#addPic').before(html);

                    uploadImg.previewQueue.push(id);

                    // 图片已经上传了 8 张，隐藏 + 号
                    if (uploadImg.countUpload() >= uploadImg.maxUpload) {
                        jq('#addPic').hide();
                        jq('.iconSendImg').addClass('fail');
                    }
                    //更新剩余上传数
                    setTimeout(function(){
                        uploadImg.uploadRemaining();
                    }, 400);

                }

                // 把输入框清空
                jq(this).val('');
            });

            jq('.photoList').on('click', '.cBtn', function() {
                // var result = confirm('取消上传这张图片?');
                // if (!result) {
                    // return false;
                // }
                var id = jq(this).attr('_id');
                // 取消这个请求
                if (uploadImg.xhr[id]) {
                    uploadImg.xhr[id].abort();
                }
                // 图片删除
                jq('#li' + id).remove();
                // 表单中删除
                jq('#input' + id).remove();
                uploadImg.uploadInfo[id] = null;
                //如果删除的微视，添加微视图标高亮
                if(id == 'video'){
                    jq('.iconVideo').addClass('iconVideoOn');
                }
                //如果删除的微视，添加微视图标高亮
                if(id == 'video'){
                    jq('.iconVideo').addClass('iconVideoOn');
                }

                // 图片变少了，显示+号
                if (uploadImg.countUpload() < uploadImg.maxUpload) {
                    jq('#addPic').show();
                    jq('.iconSendImg').removeClass('fail');
                }
                //更新剩余上传数
                uploadImg.uploadRemaining();

                //当删除所有图片后隐藏添加图片的图标加号
                if(jq('.photoList').find('li').length < 2){
                    jq('.photoList').hide();
                    jq('.sendCon').css('height', exports.contentHeight);
                }
            });

        },

        init: function() {

            exports.contentHeight = jq('.sendCon').height();

            var storageTitleKey = "topic_title",
                storageConKey = "topic_content";

            jq('#title').val(localStorage.getItem(storageTitleKey));
            jq('#content').val(localStorage.getItem(storageConKey));

            timer = setInterval(function() {
                localStorage.removeItem(storageTitleKey);
                localStorage.setItem(storageTitleKey, jq('#title').val());
                localStorage.removeItem(storageConKey);
                localStorage.setItem(storageConKey, jq('#content').val());
            }, 1000);

            // 发送
            var isSubmitButtonClicked = false;
            jq('#submitButton').bind('click', function() {
                if (uploadImg.isBusy) {
                    jq.UTIL.dialog({content:'图片上传中，请稍候', autoClose:true});
                    return false;
                }
                if (isSubmitButtonClicked || !exports.checkForm()) {
                    return false;
                }
                var opt = {
                    'noMsg': false,
                    success:function(re) {
                        var status = parseInt(re.code);
                        if (status == 0) {
                            clearInterval(timer);
                            localStorage.removeItem(storageTitleKey);
                            localStorage.removeItem(storageConKey);

                            jq.UTIL.reload(re.jumpURL);
                            return false;
                        } else {
                            isSubmitButtonClicked = false;
                            jq.UTIL.dialog({content: re.msg, autoClose:true});
                        }
                    },
                    error:function(re) {
                        isSubmitButtonClicked = false;
                    },
                    'noJump': true
                };
                isSubmitButtonClicked = true;
                jq.UTIL.ajaxForm('newthread', opt, true);
                return false;
            });

            exports.initUpload();
            exports.initModal();

        },

        // 按钮模态相关
        initModal: function() {
            // 发送按钮模态
            jq('#submitButton').bind('touchstart', function() {
                jq(this).addClass('sendOn');
            }).bind('touchend', function() {
                jq(this).removeClass('sendOn');
            });
            jq('#cBtn').bind('touchstart', function() {
                jq(this).addClass('cancelOn');
            }).bind('touchend', function() {
                jq(this).removeClass('cancelOn');
            });
        },

        checkForm: function() {

            jq.each(uploadImg.uploadInfo, function(i,n) {
                if (n && !n.isDone) {
                    jq.UTIL.dialog({content:'图片上传中，请等待', autoClose:true});
                    return false;
                }
            });

            var title = jq('#title').val();
            var titleLen = jq.UTIL.mb_strlen(jq.UTIL.trim(title));
            if (titleLen < 7) {
                jq.UTIL.dialog({content:'话题字数有点少', autoClose:true});
                return false;
            }
            if (titleLen > 180) {
                jq.UTIL.dialog({content:'话题最好不要超过60字，复杂话题可以在描述中说明', autoClose:true});
                return false;
            }

            var content = jq('#content').val();
            var contentLen = jq.UTIL.mb_strlen(jq.UTIL.trim(content));
            if (contentLen > 3072) {
                jq.UTIL.dialog({content:'描述最好不要超过1024字', autoClose:true});
                return false;
            }

            return true;
        }

    }

    exports.init();

});
