use std::convert::TryInto;

#[no_mangle]
pub fn cipher(msg: *const i8, key: *const i8, buf: *mut i8, msg_len: usize, key_len: usize){
    let msg = unsafe { std::slice::from_raw_parts(msg, msg_len) };
    let key = unsafe { std::slice::from_raw_parts(key, key_len) };
    for i in 0..msg_len {
        unsafe {
            *buf.offset(i.try_into().unwrap()) = msg[i] ^ key[i % key_len];
        }
    }
}
