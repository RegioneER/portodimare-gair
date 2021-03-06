/*globals define: true, requirejs: true */

requirejs.config({
    baseUrl: '/static/js/',
    shim: {
        'underscore': { exports: '_'}
    },
    paths: {
        'upload': 'upload',
        'templates': 'templates',
        'progress': 'jquery.ajax-progress'
    }
});


define(['upload/upload'], function (upload) {
    'use strict';

    $(function () {
        upload.initialize({
            form: '#file-uploader',
            dropZone: '#drop-zone',
            file_queue: '#file-queue',
            clear_button: '#clear-button',
            upload_button: '#upload-button'
        });
    });
});
