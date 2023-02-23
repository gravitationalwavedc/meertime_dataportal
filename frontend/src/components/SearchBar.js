import React, { useEffect, useState } from 'react';

const handleDebounce = (func, wait, immediate) => {
    let timeout = null;

    return () => {
        const later = () => {
            timeout = null;

            if (!immediate) {
                func.apply();
            }
        };

        const callNow = immediate && !timeout;

        clearTimeout(timeout);

        timeout = setTimeout(later, wait || 0);

        if (callNow) {
            func.apply();
        }
    };
};

const SearchBar = ({ query, className, style, placeholder, tableId, srText, delay, onSearch, rememberSearch }) => {
    const [searchText, setSearchText] = useState(query ? query.search : '');

    useEffect(() => {
        onSearch(searchText);
        if(rememberSearch) {
            const url = new URL(window.location.href);
            url.searchParams.set('search', searchText);
            window.history.pushState({}, '', url);
        }
    }, [searchText, rememberSearch, onSearch]);

    const onChangeValue = (e) => {
        setSearchText(e.target.value);
    };

    const onKeyup = () => {
        const debounceCallback = handleDebounce(() => {
            onSearch(searchText);
        }, delay);
        debounceCallback();
    };

    return (
        <label
            htmlFor={`search-bar-${tableId}`}
            className="search-label"
        >
            <span id={`search-bar-${tableId}-label`} className="sr-only">
                {srText}
            </span>
            <input
                id={`search-bar-${tableId}`}
                type="text"
                style={style}
                aria-labelledby={`search-bar-${tableId}-label`}
                onKeyUp={() => onKeyup()}
                onChange={onChangeValue}
                className={`form-control ${className}`}
                value={searchText}
                placeholder={placeholder || SearchBar.defaultProps.placeholder}
            />
        </label>
    );
};

SearchBar.defaultProps = {
    className: '',
    style: {},
    placeholder: 'Search',
    delay: 250,
    searchText: '',
    tableId: '0',
    srText: 'Search this table',
    remeberSearch: false,
};

export default SearchBar;