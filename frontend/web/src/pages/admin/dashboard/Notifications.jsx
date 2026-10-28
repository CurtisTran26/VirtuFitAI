import React from 'react';
import ApiUnavailable from '../../../components/ApiUnavailable';

const Page = ({ isHidden = false }) => <div className={isHidden ? 'hidden' : ''}><ApiUnavailable title="Thông báo quản trị" detail="Management API hiện chưa có endpoint thông báo." /></div>;

export default Page;
