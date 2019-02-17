$(document).ready(function () {

	// alert('hi');

	// $('#likes').click(function () {
	// 	var catid;
	// 	catid = $(this).attr("data-catid");
	// 	$.get('/rango/like_category/', { category_id: catid }, function (data) {
	// 		$('#like_count').html(data);
	// 		$('#likes').hide();
	// 	});
	// });


	// $('#suggestion').keyup(function () {
	// 	var query;
	// 	query = $(this).val();
	// 	$.get('/rango/suggest_category/', { suggestion: query }, function (data) {
	// 		$('#cats').html(data);
	// 	});
	// });


	// $('.r-add').click(function () {
	// 	var catid = $(this).attr("data-catid");
	// 	var url = $(this).attr("data-url");
	// 	var title = $(this).attr("data-title");
	// 	var me = $(this)
	// 	$.get('/rango/auto_add_page/', { category_id: catid, url: url, title: title }, function (data) {
	// 		$('#pages').html(data);
	// 		me.hide();
	// 	});
	// });
	// $('select[name=industry]').change(function () {
	// 	industry_id = $(this).val();
	// 	request_url = '/getclients/' + industry_id + '/';
	// 	$.ajax({
	// 		url: request_url,
	// 		success: function (data) {
	// 			$.each(data, function (index, text) {
	// 				alert(data);
	// 				$('select[name=showrooms]').append(
	// 					$('<option></option>').val(index).html(text)
	// 				);
	// 			};
	// 		});
	// 	}
	$('select[name=industry]').change(function () {
		// alert("yes");
		industry_id = $(this).val();
		request_url = '/getclients/' + industry_id + '/';
		$.ajax({
			url: request_url,
			success: function (data) {
				debugger;
				// alert(data);
				$('select[name=client]').empty();
				$.each(data, function (index, item) {
					$('select[name=client]').append(
						$('<option></option>').val(item.id).html(item.client_name)
					);
				});
			}
		});
		return false;
	})

});
