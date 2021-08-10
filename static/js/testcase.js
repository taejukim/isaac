function createGrid(data) {
    this.grid = new Grid({
        el: document.getElementById('grid'), // Container element
        columnOptions: {
            minWidth: 80
        },
        rowHeight: 30,
        minRowHeight: 20,
        bodyHeight: 'auto',

        columns: [{
                header: 'ID',
                name: 'testcase_id',
                width: 'auto',
                minWidth: 100,
                sortable: true,
                sortingType: 'desc',
                filter: 'text'
            },
            {
                header: 'Testcase',
                name: 'summary',
                minWidth: 200,
                sortable: true,
                sortingType: 'desc',
                filter: 'text'
            },
            {
                header: 'Priority',
                name: 'priority',
                minWidth: 100,
                width: 'auto',
                sortable: true,
                sortingType: 'desc',
                filter: 'text'
            },
            {
                header: 'Author',
                name: 'author',
                minWidth: 100,
                width: 'auto',
                sortable: true,
                sortingType: 'desc',
                filter: 'text'
            }
        ],
        data: data
    });

    Grid.applyTheme('clean')
    grid.on('focusChange', (ev) => {
        row = grid.getRow(ev.rowKey).testcase_id
        get_testcase(row)
        console.log(ev.rowKey)
    })
    return grid;
}

// ajax
function module_change(module_id) {

    console.log(module_id);
    var $function_list = $("#function_select");
    console.log($function_list);

    $function_list.empty();
    if (module_id == "") {
        function_list.append("<option value='all'>전체</option>");
        return;
    }
    $.ajax({
        type: "POST",
        url: "functions",
        async: false,
        data: {
            service_id: current_service_id,
            module_id: module_id
        },
        dataType: "json",
        success: function (jdata) {
            if (jdata.data.length == 0) {
                $function_list.append("<option value='all'>전체</option>");
            } else {
                $function_list.append("<option value='all'>전체</option>");
                $(jdata.data).each(function (i) {
                    $function_list.append("<option value='" + jdata.data[i].function_id + "'>" +
                        jdata.data[i].function_name + "</option>");
                });
            }
        },
        error: function (xhr) {
            console.log(xhr.responseText);
            alert("Get function list error");
            return;
        }
    });
    this.module_id = module_id;
    change_grid_data(this.module_id, 'all')
}

function function_change(function_id) {
    console.log(function_id, module_id);
    this.function_id = function_id;
    change_grid_data(this.module_id, this.function_id)
}

function change_grid_data(module_id, function_id) {
    $.ajax({
        type: "POST",
        url: "testcases",
        async: false,
        data: {
            service_id: current_service_id,
            module_id: module_id,
            function_id: function_id,
        },
        dataType: "json",
        success: function (jdata) {
            testcase_list = jdata.data
            grid.resetData(testcase_list)
        },
        error: function (xhr) {
            console.log(xhr.responseText);
            alert("Get function list error");
            return;
        }
    });
}

function get_testcase(testcase_id) {
    $.ajax({
        type: "POST",
        url: "testcase/" + testcase_id,
        dataType: "html",
        success: function (data) {
            $(".testcaseWrapper").empty()
            $(".testcaseWrapper").append(data)
        },
        error: function (xhr) {
            console.log(xhr.responseText);
            alert("Get function list error");
            return;
        }
    })
}