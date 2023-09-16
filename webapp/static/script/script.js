function format(d) {
  // `d` is the original data object for the row
  return (
    '<tr>' +
        '<td>Email Body:</td>' +
        '<td>' + d["5"] + '</td>'+
      '</tr>'
  );
}



$(document).ready(function() {

  if ($('#logtable')) {
  var table = $('#emailtable').DataTable({
      
    info: true,
    ordering: true,
    paging: true,
    searching: true,
    
        "columns": [  //Read a DOM sourced table into data objects
        {
            className: 'dt-control',
            orderable: false,
            data: null,
            defaultContent: ''
        },
        { data: "id" },   
          { data: "to" },
          { data: "from" },
          { data: "subject" },
          { "visible": false, "targets": 5 },  //Hiding the body column
          { data: "open"},
      ],
  });

// Add event listener for opening and closing details
  table.on('click', 'td.dt-control', function (e) {
    let tr = e.target.closest('tr');
    let row = table.row(tr);
 
    if (row.child.isShown()) {
        // This row is already open - close it
        row.child.hide();
    }
    else {
        // Open this row
        row.child(format(row.data())).show();
    }
});

  }

});


$(document).ready(function() {
  if ($('#logtable')) {
  var logtable = $('#logtable').DataTable({

    info: true,
    ordering: true,
    paging: true,
    searching: true,

        "columns": [                //Read a DOM sourced table into data objects:
          { data: "id" },
          { data: "date" },
          { data: "time" },
          { data: "to" },
          { data: "from" },
          { data: "subject" },
          { data: "message" },
          { data: "type" },
          { data: "Action",
          render: function (data, type, row) { //Checks what value is in Action and Assigns colour
            var color = 'black';
            if (data === 'Allowed') {
              color = '#62F5BC';
            }
            else if (data != 'a')
            color = '#f53d50';
            return '<span style="color:' + color + '">' + data + '</span>';
          } }
      ],


  });
}
} );




//var $rows = $('#table tr');
//$('#searchInput').keyup(function() 
//{
//    var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
//
//    $rows.show().filter(function() {
 //       var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
 //       return !~text.indexOf(val);
  //  }).hide();
//});