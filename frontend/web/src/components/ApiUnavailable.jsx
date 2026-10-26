import React from 'react';

const ApiUnavailable = ({ title, detail = 'Backend hiện chưa có API cho chức năng này. Dữ liệu mẫu đã được gỡ để tránh hiển thị sai.' }) => (
  <section className="rounded-xl border border-dashed border-[#394356] bg-[#151b28] p-8 text-center">
    <h2 className="text-base font-bold text-white">{title}</h2>
    <p className="mx-auto mt-2 max-w-xl text-sm text-[#9aa5ba]">{detail}</p>
  </section>
);

export default ApiUnavailable;
