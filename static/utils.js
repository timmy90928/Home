
/**
 * Send a POST request to the specified URL with the given data.
 * @param {string} url The URL to send the request to.
 * @param {Object} data The data to send in the request body.
 * @returns {Promise<Object>} A promise that resolves with the response data.
 * @example
 * <script src="{{ url_for('static', filename='utils.js') }}"></script>
 * sendRequest('/api/data', { key: 'value' })
 * .then(data => {
 *     document.getElementById('response').innerText = JSON.stringify(data);
 *      document.getElementById('response').innerText = data.message;
 * })
 * .catch(error => {
 *     console.error('Error:', error);
 })
 */
 function sendRequest(url, data) {
    return fetch(url, {
        method: 'POST',
        /// Set the Content-Type header to application/json so that the server knows to expect JSON data in the request body. 
        headers: {
            'Content-Type': 'application/json'
        },
        /// Convert the data to a JSON string and send it in the request body.
        body: JSON.stringify(data)
    })
    /// When the response is received, parse it as JSON and return the result.
    .then(response => response.json());
/**
@app.route('/api/data', methods=['POST'])
def get_data():
    if request.method == 'POST':
        data = request.json  # 獲取請求中的 JSON 數據
        # 處理數據並返回響應
        response = {'message': 'Received!', 'data': data}
        return jsonify(response)
    return jsonify({'message': 'Send a POST request!'})
 */
}

/**
     * Convert a dictionary to an array of objects.
     * @param {Object} dictionary
     * @returns {Array<Object>}
     */
function dictionaryToArrayOfObjects(dictionary) {
    return Object.keys(dictionary)
}   

/**
 * Dynamically populate a select element with options.
 * @param {string} id The id of the select element to populate.
 * @param {array} option_array The array of options to add to the select element.
 * @param {string} defaultOptionText The text for the default option.
 * @param {boolean} otherOp Whether to include an "other" option.
 */
function select_option(id, option_array, defaultOptionText, otherOp) {
    var select = document.getElementById(id);
    // Clear old options.
    select.innerHTML = '';

    // Add a default "Please select a category" option.
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.disabled = true;
    defaultOption.selected = true;
    defaultOption.textContent = defaultOptionText;
    select.appendChild(defaultOption);

    // Dynamically add new category options.
    option_array.forEach(data => {
        const option = document.createElement('option');
        option.value = data;
        option.textContent = data;
        select.appendChild(option);
    });

    if (otherOp) {
        const otherOption = document.createElement('option');
        otherOption.value = '其他';
        otherOption.textContent = '其他';
        select.appendChild(otherOption);
    }
}


class accounting {
    /**
     * @param {document} document The document object.
     */
    constructor(document) {
        this.ie_selects = document.querySelectorAll('input[name="ie"]');
        this.i_selects = document.getElementById('i');
        this.e_selects = document.getElementById('e');
        this.detail_select = document.getElementById('Detail');
        this.date = document.getElementById('Date');
        this.category_select = document.getElementById('Category');
        this.today = new Date().toISOString().split('T')[0];
        this.categories
        this.amount = document.getElementById('Amount');
        this.note = document.getElementById('note');
    }
    /**
     * Dynamically populate the select elements for accounting page.
     */
    DynamicSelect() {
        this.date.value = this.today;
        
        this.ie_selects.forEach(radio => {
            radio.addEventListener('change', (event) => {
                sendRequest('/accounting/getCategories', {'ie':event.target.value}) // Get the value of the selected button.
                .then(data => {
                    this.categories = data.categories;
                    var categories_array = dictionaryToArrayOfObjects(this.categories);
                    select_option('Category', categories_array,'請選擇類別');
                    select_option('Detail_list', [],'請選擇細項');
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        });
        this.category_select.addEventListener('change', (event) => {
            select_option('Detail_list', this.categories[event.target.value],'請選擇細項');
        })
        }
    /**
     * @param {string} datas The document object.
     */
    default(datas) {
        const datas_list = datas.replace('(', '').replace(')', '').replace(/'/g,'').replace(/\//g,'-').split(', ');
        console.log(datas_list);
        this.date.value = datas_list[1];
        if (datas_list[2] === '支出') {
            this.e_selects.checked = true;
        }else {
            this.i_selects.checked = true;
        };

        select_option('Category', [],datas_list[3]);
        this.detail_select.value = datas_list[4];
        select_option('Detail', [],datas_list[4]);
        this.amount.value = datas_list[5];
        this.note.value = datas_list[6];
    }
}

/**
 * Confirm whether to delete a record before performing the delete action.
 * @param {string} class_name The class name of the links to add the event listener to.
 * @example
 * <a href="#" class="small-red-button" name="{{data_list[0]}}">刪除</a>
 * document.addEventListener('DOMContentLoaded', () => { 
        confirm_delete('.small-red-button');
    })
 */
function confirm_delete(class_name) {
    document.querySelectorAll(class_name).forEach(link => {
        link.addEventListener('click', function(e) {
            var name = '這個';
            if (e.target.name){
                name = e.target.name
            }
            var cf = confirm('確定要刪除 '+name+' 嗎？');
            if (!cf) {
                e.preventDefault();
            }
        });
    });
}
