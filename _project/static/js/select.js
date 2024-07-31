function selection(){
    let searchInput = document.getElementById('prod_input')
    let kind_input = document.getElementById('kind_input')
    let price_input = document.getElementById('price_input')
    let itemID = document.getElementById('itemID')
    let searchRes = document.getElementById('search_res')
    let suplliersul = document.getElementById('suplliersul')
    
    let drop ='down';
    searchInput.onkeyup=()=>{
        if(searchInput.value!=''){
        searchRes.style.display='block'
        let filter = searchInput.value.toUpperCase();
        let tr= suplliersul.getElementsByTagName('tr');
                    for(var i=0; i<tr.length; i++){
                        let td = tr[i].getElementsByTagName('td')[0];
                        td.onclick=()=>{
                            const metakind = td.getAttribute('metakind')
                            kind_input.value = metakind
                            const metaprice = td.getAttribute('metaprice')
                            price_input.value = metaprice
                            const metaid = td.getAttribute('metaid')
                            itemID.value = metaid
                            searchInput.value = td.textContent
                            searchRes.style.display='none'
                        }
                        if(td){
                            let txtvalue = td.textContent;
                            if(txtvalue.toLocaleUpperCase().indexOf(filter)>-1){
                                tr[i].style.display='';
                                
                            }else{   
                                tr[i].style.display='none';
                            }
                        }
                        
                    }
        }else{searchRes.style.display='none'}
    }
    }
    