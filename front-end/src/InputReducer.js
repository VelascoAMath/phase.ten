
export default function inputReducer(state, action) {

    switch(action.type) {
        case 'change-input': {
            localStorage.setItem(action.key, action.value);
            return {...state, [action.key]: action.value};
        }
        case 'set-state': {
            for(const [key, val] of Object.entries(action.nextState)){
                localStorage.setItem(key, JSON.stringify(val));
            }
            return action.nextState;
        }
        case '2': {
            alert('2');
            return state;
        }
        default: {
            console.log(state);
            console.log(action);
            return state;
        }
    }
}