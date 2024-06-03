
export default function inputReducer(inputs, action) {

    switch(action.type) {
        case 'change-input': {
            localStorage.setItem(action.key, action.value);
            return {...inputs, [action.key]: action.value};
        }
        case 'set-state': {
            for(const [key, val] of Object.entries(action.nextState)){
                localStorage.setItem(key, JSON.stringify(val));
            }
            return action.nextState;
        }
        case '2': {
            alert('2');
            return inputs;
        }
        default: {
            console.log(inputs);
            console.log(action);
            return inputs;
        }
    }
}